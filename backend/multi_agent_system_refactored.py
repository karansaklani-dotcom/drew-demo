"""
Refactored Multi-Agent System for Drew - Using LangChain Tools
Each agent is a proper LangGraph agent with tool calling capabilities
"""
import uuid
import asyncio
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
    
    def __init__(self, llm: ChatOpenAI, agent_tools: AgentTools, state_callback=None):
        # Bind tools to LLM
        self.llm = llm.bind_tools(recommendation_tools)
        self.tools = agent_tools
        self.state_callback = state_callback  # Callback to yield states immediately
        
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
        planning_state = {
            "agent": "recommendation",
            "status": "planning",
            "message": "📋 Analyzing your requirements..."
        }
        agent_states.append(planning_state)
        state["agent_states"] = agent_states
        
        # Yield state immediately if callback is set
        if self.state_callback:
            await self.state_callback(planning_state)
        
        # Generate project name and description using LLM
        project_name = "Your Activity Project"
        project_description = state['user_prompt'][:100]
        
        try:
            # Build conversation context from recent messages
            conversation = "\n".join([
                f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
                for msg in state.get("messages", [])[-5:]
            ])
            
            # Ask LLM to generate project name and description
            analysis_prompt = f"""Based on this user request, create a catchy project name and description:

User: {state['user_prompt']}

Previous context: {conversation}

Provide:
1. Project Name (4-6 words, catchy and descriptive title)
2. Project Description (1 sentence summary that captures the essence)

Format your response as:
PROJECT_NAME: <name>
PROJECT_DESCRIPTION: <description>

Example:
PROJECT_NAME: Team Building Adventure Day
PROJECT_DESCRIPTION: A fun-filled day of team building activities for your group."""
            
            analysis_response = await self.llm.ainvoke([
                SystemMessage(content="You are an expert at creating catchy, descriptive project names and descriptions for activity planning."),
                HumanMessage(content=analysis_prompt)
            ])
            
            # Parse response
            content = analysis_response.content
            for line in content.split("\n"):
                if line.startswith("PROJECT_NAME:"):
                    project_name = line.split("PROJECT_NAME:")[1].strip().strip('"').strip("'")
                elif line.startswith("PROJECT_DESCRIPTION:"):
                    project_description = line.split("PROJECT_DESCRIPTION:")[1].strip().strip('"').strip("'")
            
            # Store in metadata
            if "metadata" not in state:
                state["metadata"] = {}
            state["metadata"]["suggested_project_name"] = project_name
            state["metadata"]["suggested_project_description"] = project_description
            
            logger.info(f"Generated project name: {project_name}")
            logger.info(f"Generated project description: {project_description}")
        except Exception as e:
            logger.error(f"Error generating project name: {e}", exc_info=True)
            # Fallback to simple extraction
            prompt_words = state['user_prompt'].split()[:6]
            if len(prompt_words) >= 3:
                project_name = " ".join(prompt_words).title()
                if len(project_name) > 50:
                    project_name = project_name[:47] + "..."
            state["metadata"]["suggested_project_name"] = project_name
            state["metadata"]["suggested_project_description"] = project_description
        
        # System prompt
        system_prompt = """You are an expert activity recommendation agent. Your job is to:

1. Understand the user's requirements (group size, location, budget, preferences)
2. Search for relevant activities using SEMANTIC SEARCH with the search_activities tool
3. Evaluate each activity using the reflect_on_activity tool
4. Create recommendations for good matches using the create_recommendation tool

IMPORTANT - SEMANTIC SEARCH APPROACH:
- search_activities uses PURE SEMANTIC SEARCH - no filters needed
- Include ALL requirements in your search query as natural language
- Example: "team building activities for 15 people in San Francisco with budget under $100"
- The semantic search will find activities that match the meaning of your query
- You can search multiple times with different phrasings if needed

WORKFLOW:
1. Search first with a comprehensive query
2. Reflect on top results to evaluate fit
3. Create recommendations for activities with good match scores (>0.5)
4. IMPORTANT: Create exactly 4 recommendations (no more, no less)
5. CUSTOMIZE each recommendation with a title and description that fits the user's specific use case
6. Provide clear reasoning for each recommendation
7. ALWAYS use generate_conversational_response tool after creating recommendations to provide a warm, engaging response to the user

CUSTOMIZATION IS KEY:
- Always provide customized_title that tailors the activity name to their needs
- Always provide customized_description that explains how it meets their specific requirements
- Example: User wants "Christmas party for 15 people"
  * Original: "Corporate Yoga Session"
  * Customized Title: "Festive Holiday Yoga & Wellness Experience"
  * Customized Description: "Perfect for your 15-person Christmas celebration! We'll incorporate holiday themes, festive music, and team bonding exercises that create a joyful, relaxing experience for your group."

CONVERSATIONAL RESPONSES:
- After creating recommendations, ALWAYS call generate_conversational_response tool
- This creates a warm, friendly response that makes users feel heard and excited
- The tool will generate a natural, conversational message based on the recommendations you created

Available tools:
- search_activities(query, limit): Pure semantic search - include all requirements in query
- reflect_on_activity(activity_id, user_requirements): Evaluate activity match
- create_recommendation(activity_id, reason, score, customized_title, customized_description): Add activity to project
- generate_conversational_response(user_request, recommendations_summary, number_of_recommendations): Generate warm, conversational response to user"""
        
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
                
                # Extract final response - use LLM response if we have one, otherwise use fallback
                if response.content:
                    state["final_response"] = response.content
                elif not state.get("final_response"):
                    # If we have recommendations but no response, generate one
                    if len(recommendations_created) > 0:
                        state["final_response"] = f"I've added {len(recommendations_created)} great activity recommendations to your project! Check them out - they're all tailored to what you're looking for."
                    else:
                        state["final_response"] = "I've added some great activity recommendations to your project!"
                break
            
            # Execute tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                
                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                
                # Update agent state based on tool
                new_state = None
                if tool_name == "search_activities":
                    new_state = {
                        "agent": "recommendation",
                        "status": "searching",
                        "message": f"🔍 Searching for activities..."
                    }
                elif tool_name == "reflect_on_activity":
                    new_state = {
                        "agent": "recommendation",
                        "status": "reflecting",
                        "message": f"🤔 Evaluating activities..."
                    }
                elif tool_name == "create_recommendation":
                    # Check if we've reached the limit of 4 recommendations
                    if len(recommendations_created) >= 4:
                        logger.info("Reached maximum of 4 recommendations, stopping agent")
                        # Add a message to stop the agent
                        stop_message = AIMessage(content="I've created 4 recommendations. That's the maximum number of recommendations I can add to this project.")
                        messages.append(stop_message)
                        # Break out of tool calls loop
                        break
                    
                    new_state = {
                        "agent": "recommendation",
                        "status": "adding",
                        "message": f"➕ Adding recommendation..."
                    }
                elif tool_name == "generate_conversational_response":
                    new_state = {
                        "agent": "recommendation",
                        "status": "responding",
                        "message": f"💬 Crafting response..."
                    }
                
                if new_state:
                    agent_states.append(new_state)
                    state["agent_states"] = agent_states
                    # Yield state immediately if callback is set
                    if self.state_callback:
                        logger.info(f"Calling state_callback with: {new_state}")
                        await self.state_callback(new_state)
                    else:
                        logger.warning("state_callback is None, state will not be streamed")
                
                # Execute tool
                try:
                    tool = self.tool_map.get(tool_name)
                    if tool:
                        # Call the tool function
                        tool_result = await tool.ainvoke(tool_args)
                        
                        # Track recommendation after successful creation
                        if tool_name == "create_recommendation":
                            recommendations_created.append(tool_args)
                            # Check if we've reached the limit after creating this recommendation
                            if len(recommendations_created) >= 4:
                                logger.info("Reached maximum of 4 recommendations, prompting for conversational response")
                                # Add a message to guide the agent to generate conversational response
                                guide_message = AIMessage(content="I've created 4 recommendations. Now I should use the generate_conversational_response tool to create a warm, friendly response for the user.")
                                messages.append(guide_message)
                                
                                # Build recommendations summary for the tool
                                # The tool_args contain activity_id, reason, score, customized_title, customized_description
                                rec_summary = "\n".join([
                                    f"- {rec.get('customized_title', 'Activity')}: {rec.get('reason', 'Great activity')}"
                                    for rec in recommendations_created
                                ])
                                
                                # Add a hint message to encourage using the tool
                                hint_message = HumanMessage(content=f"Now generate a conversational response using the generate_conversational_response tool. User request: {state['user_prompt']}. Recommendations created: {len(recommendations_created)}. Summary: {rec_summary}")
                                messages.append(hint_message)
                        
                        # Handle conversational response tool - use its output as final response
                        if tool_name == "generate_conversational_response":
                            # Use the tool result as the final response
                            state["final_response"] = str(tool_result)
                            logger.info(f"Generated conversational response: {str(tool_result)[:200]}...")
                        
                        # Add tool result to messages
                        tool_message = ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_call['id']
                        )
                        messages.append(tool_message)
                        
                        logger.info(f"Tool result: {str(tool_result)[:200]}...")
                        
                        # Break out of tool calls loop if we've reached the limit
                        if tool_name == "create_recommendation" and len(recommendations_created) >= 4:
                            # Break out of tool calls loop and main while loop
                            break
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
            
            # Break out of main while loop if we've reached 4 recommendations
            # But only if we haven't already generated a conversational response
            if len(recommendations_created) >= 4 and not state.get("final_response"):
                logger.info("Reached maximum of 4 recommendations, generating conversational response")
                # Generate conversational response if not already done
                # The agent should call the tool, but if it doesn't, we'll use a fallback
                if not state.get("final_response"):
                    state["final_response"] = "I've added 4 great activity recommendations to your project! Check them out - they're all tailored to what you're looking for."
                break
        
        # Update completion state
        completed_state = {
            "agent": "recommendation",
            "status": "completed",
            "message": f"✅ Added {len(recommendations_created)} recommendations"
        }
        agent_states.append(completed_state)
        state["agent_states"] = agent_states
        
        # Yield state immediately if callback is set
        if self.state_callback:
            await self.state_callback(completed_state)
        
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
        
        # State callback queue for streaming
        self.state_queue = None
        
        # Initialize sub-agents (will be set with callback in stream method)
        self.recommendation_agent = None
        self.itinerary_agent = ItineraryBuilderAgent(self.llm, tools)
        self.offerings_agent = OfferingsAgent(self.llm, tools)
        
        # Build graph
        self.checkpointer = MemorySaver()
        self.graph = None  # Will be built in stream method with callback
    
    def _build_graph(self, state_callback=None) -> StateGraph:
        """Build the supervisor workflow graph"""
        workflow = StateGraph(AgentState)
        
        # Create recommendation agent with callback if provided
        if state_callback:
            self.recommendation_agent = RecommendationAgentWithTools(self.llm, self.tools, state_callback)
        else:
            self.recommendation_agent = RecommendationAgentWithTools(self.llm, self.tools)
        
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
    
    async def stream(
        self,
        prompt: str,
        user_id: str,
        project_id: str,
        thread_id: Optional[str] = None
    ):
        """Stream the supervisor agent execution in real-time"""
        
        # Use existing thread_id if provided, otherwise create a new one
        if not thread_id:
            thread_id = str(uuid.uuid4())
        
        logger.info(f"Streaming refactored supervisor for project {project_id}")
        
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
        
        # Run graph with streaming
        config = {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": f"project_{project_id}_{thread_id}"
            }
        }
        
        try:
            # Create a callback queue to yield states immediately
            state_queue = asyncio.Queue()
            
            # Create callback function that yields states immediately
            async def state_callback(state):
                await state_queue.put(state)
            
            # Build graph with callback
            self.graph = self._build_graph(state_callback)
            
            # Track final state
            final_state = None
            
            # Start streaming task
            async def stream_graph():
                nonlocal final_state
                async for event in self.graph.astream(initial_state, config):
                    for node_name, node_state in event.items():
                        # Track final state (last event is the final state)
                        final_state = node_state
            
            # Run graph streaming and state queue processing concurrently
            graph_task = asyncio.create_task(stream_graph())
            
            # Process states from queue as they arrive
            while True:
                try:
                    # Wait for state with timeout
                    state = await asyncio.wait_for(state_queue.get(), timeout=0.1)
                    logger.info(f"Yielding agent_state: {state}")
                    yield {"type": "agent_state", "state": state}
                except asyncio.TimeoutError:
                    # Check if graph task is done
                    if graph_task.done():
                        # Process any remaining states in queue
                        while not state_queue.empty():
                            try:
                                state = state_queue.get_nowait()
                                logger.info(f"Yielding remaining agent_state: {state}")
                                yield {"type": "agent_state", "state": state}
                            except asyncio.QueueEmpty:
                                break
                        break
                    # Continue waiting
                    continue
            
            # Wait for graph to complete
            await graph_task
            
            # Generate project name from prompt or use a default
            project_name = "Your Activity Project"
            project_description = prompt[:100]
            
            # Try to extract a meaningful project name from the prompt
            # Take first 4-6 words as project name, or use a generated one
            prompt_words = prompt.split()[:6]
            if len(prompt_words) >= 3:
                # Create a title from the prompt
                project_name = " ".join(prompt_words).title()
                # Limit to 50 characters
                if len(project_name) > 50:
                    project_name = project_name[:47] + "..."
            
            # Use metadata if available
            metadata = final_state.get("metadata", {})
            if metadata.get("suggested_project_name"):
                project_name = metadata["suggested_project_name"]
            if metadata.get("suggested_project_description"):
                project_description = metadata["suggested_project_description"]
            
            # Yield final response
            yield {
                "type": "complete",
                "message": final_state["final_response"],
                "recommendations": final_state["recommendations"],
                "agentsUsed": final_state["agent_history"],
                "threadId": thread_id,
                "projectId": project_id,
                "projectName": project_name,
                "projectDescription": project_description,
                "metadata": {
                    "userContext": final_state.get("user_context", {}),
                    "recommendationCount": len(final_state["recommendations"])
                }
            }
        
        except Exception as e:
            logger.error(f"Error in supervisor stream: {e}", exc_info=True)
            yield {
                "type": "error",
                "error": str(e)
            }
    
    async def run(
        self,
        prompt: str,
        user_id: str,
        project_id: str,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run the supervisor agent (non-streaming)"""
        
        # Use existing thread_id if provided, otherwise create a new one
        if not thread_id:
            thread_id = str(uuid.uuid4())
        
        # Build graph if not already built
        if self.graph is None:
            self.graph = self._build_graph()
        
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
