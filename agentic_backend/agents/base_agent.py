"""Base agent implementation with LangGraph."""

import logging
from typing import Annotated, Sequence, TypedDict, Optional, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
from emergentintegrations.llm.chat import LlmChat, UserMessage
import operator

from config import config
from checkpointing import get_checkpointer
from threads.manager import ThreadManager
from threads.models import MessageType

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    thread_id: str
    user_preferences: Dict[str, Any]
    context: str
    tool_calls: List[Dict[str, Any]]
    sub_agents: Dict[str, Any]


class BaseAgent:
    """Base agent with checkpointing and state management."""
    
    def __init__(
        self,
        agent_type: str = "base",
        system_message: Optional[str] = None,
        tools: Optional[List[BaseTool]] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None
    ):
        self.agent_type = agent_type
        self.system_message = system_message or "You are a helpful AI assistant."
        self.tools = tools or []
        
        # LLM configuration
        self.api_key = api_key or config.llm.api_key
        self.model = model or config.llm.default_model
        self.provider = provider or config.llm.default_provider
        
        # Components
        self.thread_manager = ThreadManager()
        self.checkpointer: Optional[AsyncMongoDBSaver] = None
        self.graph = None
        
    async def initialize(self):
        """Initialize the agent."""
        try:
            # Initialize thread manager
            await self.thread_manager.initialize()
            
            # Initialize checkpointer
            self.checkpointer = await get_checkpointer()
            
            # Build the agent graph
            self.graph = await self._build_graph()
            
            logger.info(f"Agent '{self.agent_type}' initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing agent: {e}")
            raise
    
    async def _build_graph(self):
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        
        if self.tools:
            workflow.add_node("tools", ToolNode(self.tools))
        
        # Add edges
        workflow.set_entry_point("agent")
        
        if self.tools:
            workflow.add_conditional_edges(
                "agent",
                self._should_use_tools,
                {
                    "tools": "tools",
                    "end": END
                }
            )
            workflow.add_edge("tools", "agent")
        else:
            workflow.add_edge("agent", END)
        
        # Compile with checkpointer
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _agent_node(self, state: AgentState) -> AgentState:
        """Main agent processing node."""
        try:
            messages = state.get("messages", [])
            thread_id = state.get("thread_id")
            context = state.get("context", "")
            
            # Get the last message
            if not messages:
                return state
            
            last_message = messages[-1]
            
            # Build prompt with context
            prompt = last_message.content
            if context:
                prompt = f"Context:\n{context}\n\nUser: {prompt}"
            
            # Create LLM chat instance
            chat = LlmChat(
                api_key=self.api_key,
                session_id=thread_id or "default",
                system_message=self.system_message
            ).with_model(self.provider, self.model)
            
            # Get response from LLM
            response = await chat.send_message(UserMessage(text=prompt))
            response_text = response.get('content', '')
            
            # Create AI message
            ai_message = AIMessage(content=response_text)
            
            # Save message to thread if thread_id exists
            if thread_id:
                await self.thread_manager.add_message(
                    thread_id=thread_id,
                    role=MessageType.ASSISTANT,
                    content=response_text,
                    metadata={"agent_type": self.agent_type}
                )
            
            return {
                **state,
                "messages": [ai_message]
            }
            
        except Exception as e:
            logger.error(f"Error in agent node: {e}")
            error_message = AIMessage(content=f"I encountered an error: {str(e)}")
            return {
                **state,
                "messages": [error_message]
            }
    
    def _should_use_tools(self, state: AgentState) -> str:
        """Determine if tools should be used."""
        messages = state.get("messages", [])
        if not messages:
            return "end"
        
        last_message = messages[-1]
        
        # Check if the message has tool calls
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        return "end"
    
    async def invoke(
        self,
        message: str,
        thread_id: str,
        user_preferences: Optional[Dict[str, Any]] = None,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Invoke the agent with a message."""
        try:
            # Ensure thread exists
            thread = await self.thread_manager.get_thread(thread_id)
            if not thread:
                thread = await self.thread_manager.create_thread(
                    agent_type=self.agent_type
                )
                thread_id = thread.id
            
            # Save user message to thread
            await self.thread_manager.add_message(
                thread_id=thread_id,
                role=MessageType.USER,
                content=message
            )
            
            # Get context for the agent
            context = await self.thread_manager.get_context_for_agent(thread_id)
            
            # Prepare initial state
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "thread_id": thread_id,
                "user_preferences": user_preferences or {},
                "context": context,
                "tool_calls": [],
                "sub_agents": {}
            }
            
            # Prepare config for checkpointing
            run_config = {
                "configurable": {
                    "thread_id": thread_id
                }
            }
            
            if config_overrides:
                run_config.update(config_overrides)
            
            # Invoke the graph
            result = await self.graph.ainvoke(initial_state, run_config)
            
            # Extract response
            messages = result.get("messages", [])
            response_message = messages[-1] if messages else None
            
            return {
                "response": response_message.content if response_message else "No response",
                "thread_id": thread_id,
                "messages": [msg.dict() if hasattr(msg, 'dict') else str(msg) for msg in messages],
                "state": result
            }
            
        except Exception as e:
            logger.error(f"Error invoking agent: {e}")
            return {
                "error": str(e),
                "thread_id": thread_id
            }
    
    async def stream(
        self,
        message: str,
        thread_id: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ):
        """Stream responses from the agent."""
        try:
            # Ensure thread exists
            thread = await self.thread_manager.get_thread(thread_id)
            if not thread:
                thread = await self.thread_manager.create_thread(
                    agent_type=self.agent_type
                )
                thread_id = thread.id
            
            # Save user message
            await self.thread_manager.add_message(
                thread_id=thread_id,
                role=MessageType.USER,
                content=message
            )
            
            # Get context
            context = await self.thread_manager.get_context_for_agent(thread_id)
            
            # Prepare initial state
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "thread_id": thread_id,
                "user_preferences": user_preferences or {},
                "context": context,
                "tool_calls": [],
                "sub_agents": {}
            }
            
            # Prepare config
            run_config = {
                "configurable": {
                    "thread_id": thread_id
                }
            }
            
            # Stream the graph execution
            async for chunk in self.graph.astream(initial_state, run_config):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error streaming from agent: {e}")
            yield {"error": str(e)}
    
    async def get_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state for a thread."""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            state = await self.graph.aget_state(config)
            return state
        except Exception as e:
            logger.error(f"Error getting state: {e}")
            return None
    
    async def update_state(
        self,
        thread_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update the state for a thread."""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            await self.graph.aupdate_state(config, updates)
            return True
        except Exception as e:
            logger.error(f"Error updating state: {e}")
            return False
