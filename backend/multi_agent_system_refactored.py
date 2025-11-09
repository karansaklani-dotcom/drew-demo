"""
Refactored Multi-Agent System for Drew - Using LangChain Tools
Each agent is a proper LangGraph agent with tool calling capabilities
"""
import uuid
from typing import List, Dict, Any, Optional, TypedDict
from datetime import datetime
import logging
import json

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from agent_tools import AgentTools
from recommendation_tools import (
    recommendation_tools,
    set_agent_tools,
    set_current_context
)

logger = logging.getLogger(__name__)

# ============================================================================
# STATE DEFINITIONS
# ============================================================================

class AgentState(TypedDict):
    """State for individual agents"""
    messages: List
    user_prompt: str
    user_id: str
    project_id: str
    thread_id: str
    
    # Context
    user_context: Dict[str, Any]
    
    # Agent tracking
    agent_history: List[str]
    
    # Results
    recommendations: List[Dict[str, Any]]
    current_recommendation_id: Optional[str]
    
    # Response
    final_response: str
    
    # Metadata
    metadata: Dict[str, Any]
    
    # Agent states for streaming
    agent_states: List[Dict[str, Any]]
    
    # Tool execution
    next_action: Optional[str]

# ============================================================================
# RECOMMENDATION AGENT WITH TOOLS
# ============================================================================

class RecommendationAgentWithTools:
    """
    Recommendation agent that uses LangChain tools for operations
    This is a proper agentic system with tool calling
    """
    
    def __init__(self, llm: ChatOpenAI, agent_tools: AgentTools):
        # Bind tools to LLM
        self.llm = llm.bind_tools(recommendation_tools)
        self.tools = agent_tools
        
        # Create tool map for execution
        self.tool_map = {tool.name: tool for tool in recommendation_tools}
        
        # Set global agent tools for tool functions
        set_agent_tools(agent_tools)
    
    async def run(self, state: AgentState) -> AgentState:
        """Execute recommendation agent with tool calling"""
        logger.info(f"🎯 Running Recommendation Agent with Tools")
        
        # Check if already ran
        if "recommendation" in state.get("agent_history", []):
            logger.warning("Recommendation agent already ran")
            return state
        
        # Set current context for tools
        set_current_context({
            'project_id': state['project_id'],
            'user_id': state['user_id']
        })
        
        # Add agent state
        agent_states = state.get("agent_states", [])
        agent_states.append({
            "agent": "recommendation",
            "status": "planning",
            "message": "📋 Analyzing your requirements..."
        })
        state["agent_states"] = agent_states
        
        # System prompt
        system_prompt = """You are an expert activity recommendation agent. Your job is to:

1. Understand the user's requirements (group size, location, budget, preferences)
2. Search for relevant activities using the search_activities tool
3. Evaluate each activity using the reflect_on_activity tool
4. Create recommendations for good matches using the create_recommendation tool

IMPORTANT: 
- Always use tools to perform actions
- Search first, then reflect on results, then create recommendations
- Only recommend activities with good match scores (>0.5)
- Provide clear reasoning for each recommendation

Available tools:
- search_activities: Find activities based on requirements
- reflect_on_activity: Evaluate if an activity matches user needs
- create_recommendation: Add an activity to the project as a recommendation"""
        
        # Build messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User request: {state['user_prompt']}")
        ]
        
        # Agent loop with tool calling
        max_iterations = 10
        iteration = 0
        recommendations_created = []
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Agent iteration {iteration}")
            
            # Call LLM
            response = await self.llm.ainvoke(messages)
            messages.append(response)
            
            # Check if we have tool calls
            if not response.tool_calls:
                # No more tool calls - agent is done
                logger.info("Agent finished - no more tool calls")
                
                # Extract final response
                state["final_response"] = response.content or "I've added some great activity recommendations to your project!"
                break
            
            # Execute tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                
                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                
                # Update agent state based on tool
                if tool_name == "search_activities":
                    agent_states.append({
                        "agent": "recommendation",
                        "status": "searching",
                        "message": f"🔍 Searching for activities..."
                    })
                elif tool_name == "reflect_on_activity":
                    agent_states.append({
                        "agent": "recommendation",
                        "status": "reflecting",
                        "message": f"🤔 Evaluating activities..."
                    })
                elif tool_name == "create_recommendation":
                    agent_states.append({
                        "agent": "recommendation",
                        "status": "adding",
                        "message": f"➕ Adding recommendation..."
                    })
                    # Track recommendation
                    recommendations_created.append(tool_args)
                
                state["agent_states"] = agent_states
                
                # Execute tool
                try:
                    tool = self.tool_map.get(tool_name)
                    if tool:
                        # Call the tool function
                        tool_result = await tool.ainvoke(tool_args)
                        
                        # Add tool result to messages
                        tool_message = ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_call['id']
                        )
                        messages.append(tool_message)
                        
                        logger.info(f"Tool result: {str(tool_result)[:200]}...")
                    else:
                        logger.error(f"Tool {tool_name} not found")
                        error_message = ToolMessage(
                            content=f"Tool {tool_name} not found",
                            tool_call_id=tool_call['id']
                        )
                        messages.append(error_message)
                    
                except Exception as e:
                    logger.error(f"Tool execution error: {e}", exc_info=True)
                    error_message = ToolMessage(
                        content=f"Error executing {tool_name}: {str(e)}",
                        tool_call_id=tool_call['id']
                    )
                    messages.append(error_message)
        
        # Update completion state
        agent_states.append({
            "agent": "recommendation",
            "status": "completed",
            "message": f"✅ Added {len(recommendations_created)} recommendations"
        })
        state["agent_states"] = agent_states
        
        # Update agent history
        agent_history = state.get("agent_history", [])
        if "recommendation" not in agent_history:
            agent_history.append("recommendation")
        state["agent_history"] = agent_history
        
        # Set recommendations count in metadata
        state["recommendations"] = recommendations_created
        
        return state

# ============================================================================
# ITINERARY BUILDER AGENT
# ============================================================================

class ItineraryBuilderAgent:
    """Agent responsible for customizing itineraries - kept simple for now"""
    
    def __init__(self, llm: ChatOpenAI, tools: AgentTools):
        self.llm = llm
        self.tools = tools
    
    async def run(self, state: AgentState) -> AgentState:
        """Execute itinerary builder agent"""
        logger.info("📅 Running Itinerary Builder Agent")
        
        # Check if already ran
        agent_history = state.get("agent_history", [])
        if "itinerary_builder" in agent_history:
            logger.warning("Itinerary builder already ran")
            return state
        
        agent_states = state.get("agent_states", [])
        agent_states.append({
            "agent": "itinerary_builder",
            "status": "started",
            "message": "Customizing itineraries..."
        })
        state["agent_states"] = agent_states
        
        # Update agent history
        if "itinerary_builder" not in agent_history:
            agent_history.append("itinerary_builder")
        state["agent_history"] = agent_history
        
        return state

# ============================================================================
# OFFERINGS AGENT
# ============================================================================

class OfferingsAgent:
    """Agent responsible for managing offerings - kept simple for now"""
    
    def __init__(self, llm: ChatOpenAI, tools: AgentTools):
        self.llm = llm
        self.tools = tools
    
    async def run(self, state: AgentState) -> AgentState:
        """Execute offerings agent"""
        logger.info("🎁 Running Offerings Agent")
        
        # Check if already ran
        agent_history = state.get("agent_history", [])
        if "offerings" in agent_history:
            logger.warning("Offerings agent already ran")
            return state
        
        agent_states = state.get("agent_states", [])
        agent_states.append({
            "agent": "offerings",
            "status": "started",
            "message": "Adding relevant offerings..."
        })
        state["agent_states"] = agent_states
        
        # Update agent history
        if "offerings" not in agent_history:
            agent_history.append("offerings")
        state["agent_history"] = agent_history
        
        return state

# ============================================================================
# SUPERVISOR AGENT
# ============================================================================

class SupervisorAgentRefactored:
    """Coordinates all sub-agents with proper tool integration"""
    
    def __init__(self, openai_api_key: str, tools: AgentTools):
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4o-mini",
            temperature=0.7
        )
        self.tools = tools
        
        # Initialize sub-agents
        self.recommendation_agent = RecommendationAgentWithTools(self.llm, tools)
        self.itinerary_agent = ItineraryBuilderAgent(self.llm, tools)
        self.offerings_agent = OfferingsAgent(self.llm, tools)
        
        # Build graph
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the supervisor workflow graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("recommendation", self.recommendation_agent.run)
        workflow.add_node("itinerary_builder", self.itinerary_agent.run)
        workflow.add_node("offerings", self.offerings_agent.run)
        
        # Set entry point
        workflow.set_entry_point("recommendation")
        
        # Simple linear flow for now
        workflow.add_edge("recommendation", "itinerary_builder")
        workflow.add_edge("itinerary_builder", "offerings")
        workflow.add_edge("offerings", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def run(
        self,
        prompt: str,
        user_id: str,
        project_id: str,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run the supervisor agent"""
        
        # Always use fresh thread_id
        thread_id = str(uuid.uuid4())
        
        logger.info(f"Running refactored supervisor for project {project_id}")
        
        # Initialize state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=prompt)],
            "user_prompt": prompt,
            "user_id": user_id,
            "project_id": project_id,
            "thread_id": thread_id,
            "user_context": {},
            "agent_history": [],
            "recommendations": [],
            "current_recommendation_id": None,
            "final_response": "",
            "metadata": {},
            "agent_states": [],
            "next_action": None
        }
        
        # Run graph
        config = {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": f"project_{project_id}_{thread_id}"
            }
        }
        
        try:
            final_state = await self.graph.ainvoke(initial_state, config)
            
            return {
                "message": final_state["final_response"],
                "recommendations": final_state["recommendations"],
                "agentsUsed": final_state["agent_history"],
                "agentStates": final_state.get("agent_states", []),
                "threadId": thread_id,
                "projectId": project_id,
                "projectName": "Your Activity Project",  # TODO: Extract from LLM
                "projectDescription": prompt[:100],  # TODO: Extract from LLM
                "metadata": {
                    "userContext": final_state.get("user_context", {}),
                    "recommendationCount": len(final_state["recommendations"])
                }
            }
        
        except Exception as e:
            logger.error(f"Error in supervisor: {e}", exc_info=True)
            return {
                "message": "I encountered an error processing your request. Please try again.",
                "recommendations": [],
                "agentsUsed": [],
                "threadId": thread_id,
                "projectId": project_id,
                "metadata": {"error": str(e)}
            }
