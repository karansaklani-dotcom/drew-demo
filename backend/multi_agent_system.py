"""
Multi-Agent System for Drew
Supervisor agent that coordinates recommendation, itinerary, and offerings agents
"""
import uuid
from typing import List, Dict, Any, Optional, TypedDict, Annotated, Literal
from datetime import datetime
import logging
import operator

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from agent_tools import AgentTools

logger = logging.getLogger(__name__)

# ============================================================================
# STATE DEFINITIONS
# ============================================================================

class SupervisorState(TypedDict):
    """State for supervisor agent"""
    messages: Annotated[List, operator.add]
    user_prompt: str
    user_id: str
    project_id: str
    thread_id: str
    
    # Context
    user_context: Dict[str, Any]
    
    # Agent routing
    next_agent: Optional[str]
    agent_history: List[str]
    
    # Results
    recommendations: List[Dict[str, Any]]
    current_recommendation_id: Optional[str]
    
    # Response
    final_response: str
    
    # Metadata
    metadata: Dict[str, Any]
    
    # Agent states for streaming
    agent_states: Annotated[List, operator.add]

# ============================================================================
# RECOMMENDATION AGENT
# ============================================================================

class RecommendationAgent:
    """Agent responsible for finding and recommending activities"""
    
    def __init__(self, llm: ChatOpenAI, tools: AgentTools):
        self.llm = llm
        self.tools = tools
    
    async def run(self, state: SupervisorState) -> SupervisorState:
        """Execute recommendation agent"""
        logger.info("🎯 Running Recommendation Agent")
        
        # Add agent state
        state["agent_states"].append({
            "agent": "recommendation",
            "status": "started",
            "message": "Analyzing your request..."
        })
        
        system_prompt = """You are a recommendation specialist. Your job is to:
1. Generate a concise project name and description from user prompt
2. Understand user requirements from their prompt and conversation history
3. Search for relevant activities using semantic search
4. Reflect on whether activities fit user needs
5. Create recommendations for the project

Extract key information:
- Group size
- Location preferences
- Budget
- Occasion/purpose
- Duration preferences
- Activity type preferences

Be conversational and helpful!"""
        
        # Build context from messages
        conversation = "\n".join([
            f"{msg.type}: {msg.content}" for msg in state["messages"][-5:]
        ])
        
        # Ask LLM to extract search parameters and generate project name
        analysis_prompt = f"""Based on this user request, extract information and create project details:

User: {state['user_prompt']}

Previous context: {conversation}

Provide:
1. Project Name (4-6 words, catchy title)
2. Project Description (1 sentence summary)
3. Search query (concise, 1-2 sentences)
4. Filters (JSON format): location, minParticipants, maxParticipants, priceMax, category
5. User context (JSON): groupSize, budget, occasion, preferences

Format:
PROJECT_NAME: <name>
PROJECT_DESCRIPTION: <description>
SEARCH_QUERY: <query>
FILTERS: <json>
CONTEXT: <json>
"""
        
        response = await self.llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=analysis_prompt)
        ])
        
        # Parse response
        content = response.content
        search_query = state["user_prompt"]
        filters = {}
        user_context = {}
        
        for line in content.split("\n"):
            if line.startswith("SEARCH_QUERY:"):
                search_query = line.split("SEARCH_QUERY:")[1].strip()
            elif line.startswith("FILTERS:"):
                try:
                    import json
                    filters = json.loads(line.split("FILTERS:")[1].strip())
                except:
                    pass
            elif line.startswith("CONTEXT:"):
                try:
                    import json
                    user_context = json.loads(line.split("CONTEXT:")[1].strip())
                except:
                    pass
        
        # Search activities
        logger.info(f"Searching with query: {search_query}, filters: {filters}")
        
        state["agent_states"].append({
            "agent": "recommendation",
            "status": "searching",
            "message": f"Searching activities with: {search_query}"
        })
        
        activities = await self.tools.search_activities(
            query=search_query,
            filters=filters if filters else None,
            limit=5
        )
        
        if not activities:
            # Generate a helpful response even when no activities found
            response_prompt = f"""The user said: "{state['user_prompt']}"

No specific activities were found. Generate a friendly, helpful response that:
1. Acknowledges their request
2. Asks clarifying questions about what they're looking for
3. Suggests being more specific (e.g., location, group size, type of activity)

Keep it warm and conversational."""
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=response_prompt)
            ])
            
            state["final_response"] = response.content
            state["next_agent"] = None
            state["agent_history"].append("recommendation")
            return state
        
        # Reflect and create recommendations
        state["agent_states"].append({
            "agent": "recommendation",
            "status": "reflecting",
            "message": f"Analyzing {len(activities)} activities for best matches..."
        })
        
        recommendations = []
        for activity in activities[:3]:  # Top 3
            # Reflect
            reflection = await self.tools.reflect_and_transform(activity, user_context)
            
            # Lower threshold to 0.3 to show more results
            if reflection["reflection"]["score"] > 0.3:
                # Create recommendation
                matched_criteria = reflection['reflection'].get('matchedCriteria', [])
                if matched_criteria:
                    reason = f"Great fit! {', '.join(matched_criteria)}"
                else:
                    reason = "This is a popular activity that might interest you"
                    
                rec = await self.tools.create_recommendation(
                    project_id=state["project_id"],
                    user_id=state["user_id"],
                    activity=activity,
                    reason_to_recommend=reason,
                    score=reflection["reflection"]["score"]
                )
                recommendations.append(rec)
                logger.info(f"Created recommendation: {rec['title']}")
        
        state["recommendations"] = recommendations
        state["user_context"] = user_context
        
        state["agent_states"].append({
            "agent": "recommendation",
            "status": "completed",
            "message": f"Created {len(recommendations)} recommendations"
        })
        
        if not recommendations:
            # Found activities but none passed reflection
            response_prompt = f"""The user said: "{state['user_prompt']}"

We found some activities but they may not be the perfect match. Generate a friendly response that:
1. Acknowledges their request
2. Suggests being more specific about preferences
3. Asks what type of activities they're interested in

Keep it encouraging and helpful."""
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=response_prompt)
            ])
            
            state["final_response"] = response.content
            state["next_agent"] = None
            state["agent_history"].append("recommendation")
            return state
        
        # Generate response
        rec_summary = "\n".join([
            f"- {rec['title']} ({rec.get('duration', 180)//60} hours): {rec.get('reasonToRecommend', 'Great activity')}"
            for rec in recommendations
        ])
        
        response_prompt = f"""Generate a friendly response to the user about these recommendations:

{rec_summary}

Keep it conversational, warm, and helpful. Mention 1-2 highlights."""
        
        response = await self.llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=response_prompt)
        ])
        
        state["final_response"] = response.content
        state["agent_history"].append("recommendation")
        
        # Decide next agent
        if recommendations and len(recommendations) > 0:
            state["next_agent"] = "itinerary_builder"
            state["current_recommendation_id"] = recommendations[0].get('id')
        else:
            state["next_agent"] = None
        
        return state

# ============================================================================
# ITINERARY BUILDER AGENT
# ============================================================================

class ItineraryBuilderAgent:
    """Agent responsible for customizing itineraries"""
    
    def __init__(self, llm: ChatOpenAI, tools: AgentTools):
        self.llm = llm
        self.tools = tools
    
    async def run(self, state: SupervisorState) -> SupervisorState:
        """Execute itinerary builder agent"""
        logger.info("📅 Running Itinerary Builder Agent")
        
        state["agent_states"].append({
            "agent": "itinerary_builder",
            "status": "started",
            "message": "Customizing activity itineraries..."
        })
        
        if not state.get("current_recommendation_id"):
            logger.warning("No recommendation to build itinerary for")
            state["next_agent"] = None
            return state
        
        # Get recommendation details
        rec = await self.tools.retrieve_recommendation_details(
            recommendation_id=state["current_recommendation_id"],
            user_id=state["user_id"]
        )
        
        current_itinerary = rec.get('itinerary', [])
        
        # Reflect on itinerary
        reflection = await self.tools.reflect_on_itinerary(
            itinerary=current_itinerary,
            user_expectations=state.get("user_context", {})
        )
        
        if not reflection["isGoodFit"] and reflection["suggestions"]:
            # Build enhanced itinerary
            system_prompt = """You are an itinerary specialist. Create a customized itinerary based on:
1. Current itinerary structure
2. User expectations
3. Suggestions for improvement

Generate an improved itinerary in JSON format."""
            
            enhance_prompt = f"""Current itinerary: {current_itinerary}
            
User expectations: {state.get('user_context', {})}

Suggestions: {reflection['suggestions']}

Create an enhanced itinerary. Return JSON array of items with: duration, title, description."""
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=enhance_prompt)
            ])
            
            # Try to parse improved itinerary
            try:
                import json
                content = response.content
                # Extract JSON from response
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                else:
                    json_str = content
                
                new_itinerary = json.loads(json_str)
                
                # Update recommendation
                await self.tools.update_recommendation_itinerary(
                    recommendation_id=state["current_recommendation_id"],
                    user_id=state["user_id"],
                    new_itinerary=new_itinerary
                )
                logger.info("Updated itinerary successfully")
            except Exception as e:
                logger.error(f"Failed to update itinerary: {e}")
        
        state["agent_history"].append("itinerary_builder")
        state["next_agent"] = "offerings"
        
        return state

# ============================================================================
# OFFERINGS AGENT
# ============================================================================

class OfferingsAgent:
    """Agent responsible for managing offerings"""
    
    def __init__(self, llm: ChatOpenAI, tools: AgentTools):
        self.llm = llm
        self.tools = tools
    
    async def run(self, state: SupervisorState) -> SupervisorState:
        """Execute offerings agent"""
        logger.info("🎁 Running Offerings Agent")
        
        state["agent_states"].append({
            "agent": "offerings",
            "status": "started",
            "message": "Adding relevant offerings..."
        })
        
        if not state.get("current_recommendation_id"):
            logger.warning("No recommendation to manage offerings for")
            state["next_agent"] = None
            return state
        
        # Get recommendation details
        rec = await self.tools.retrieve_recommendation_details(
            recommendation_id=state["current_recommendation_id"],
            user_id=state["user_id"]
        )
        
        current_offerings = rec.get('offeringIds', [])
        
        # Reflect on offerings
        reflection = await self.tools.reflect_on_offerings(
            current_offerings=current_offerings,
            user_needs=state.get("user_context", {})
        )
        
        if not reflection["areSufficient"] and reflection["needed"]:
            # Search for needed offerings
            for need in reflection["needed"]:
                offerings = await self.tools.search_offerings(query=need, limit=3)
                if offerings:
                    # Add first matching offering
                    offering_id = str(offerings[0].get('_id'))
                    if offering_id not in current_offerings:
                        current_offerings.append(offering_id)
            
            # Update recommendation
            await self.tools.update_recommendation_offerings(
                recommendation_id=state["current_recommendation_id"],
                user_id=state["user_id"],
                offering_ids=current_offerings
            )
            logger.info(f"Updated offerings: added {len(reflection['needed'])} items")
        
        state["agent_history"].append("offerings")
        state["next_agent"] = None  # End of agent chain
        
        return state

# ============================================================================
# SUPERVISOR AGENT
# ============================================================================

class SupervisorAgent:
    """Coordinates all sub-agents"""
    
    def __init__(self, openai_api_key: str, tools: AgentTools):
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4o-mini",
            temperature=0.7
        )
        self.tools = tools
        
        # Initialize sub-agents
        self.recommendation_agent = RecommendationAgent(self.llm, tools)
        self.itinerary_agent = ItineraryBuilderAgent(self.llm, tools)
        self.offerings_agent = OfferingsAgent(self.llm, tools)
        
        # Build graph and checkpointer
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the supervisor workflow graph"""
        workflow = StateGraph(SupervisorState)
        
        # Add nodes
        workflow.add_node("recommendation", self.recommendation_agent.run)
        workflow.add_node("itinerary_builder", self.itinerary_agent.run)
        workflow.add_node("offerings", self.offerings_agent.run)
        
        # Set entry point
        workflow.set_entry_point("recommendation")
        
        # Define conditional edges
        def route_next(state: SupervisorState) -> str:
            next_agent = state.get("next_agent")
            if next_agent == "itinerary_builder":
                return "itinerary_builder"
            elif next_agent == "offerings":
                return "offerings"
            else:
                return END
        
        # Add conditional routing
        workflow.add_conditional_edges(
            "recommendation",
            route_next,
            {
                "itinerary_builder": "itinerary_builder",
                "offerings": "offerings",
                END: END
            }
        )
        
        workflow.add_conditional_edges(
            "itinerary_builder",
            route_next,
            {
                "offerings": "offerings",
                END: END
            }
        )
        
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
        
        if not thread_id:
            thread_id = str(uuid.uuid4())
        
        # Initialize state
        initial_state: SupervisorState = {
            "messages": [HumanMessage(content=prompt)],
            "user_prompt": prompt,
            "user_id": user_id,
            "project_id": project_id,
            "thread_id": thread_id,
            "user_context": {},
            "next_agent": None,
            "agent_history": [],
            "recommendations": [],
            "current_recommendation_id": None,
            "final_response": "",
            "metadata": {},
            "agent_states": []
        }
        
        # Run the graph
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            final_state = await self.graph.ainvoke(initial_state, config)
            
            return {
                "message": final_state["final_response"],
                "recommendations": final_state["recommendations"],
                "agentsUsed": final_state["agent_history"],
                "agentStates": final_state.get("agent_states", []),
                "threadId": thread_id,
                "projectId": project_id,
                "metadata": {
                    "userContext": final_state.get("user_context", {}),
                    "recommendationCount": len(final_state["recommendations"])
                }
            }
        
        except Exception as e:
            logger.error(f"Error in supervisor agent: {e}", exc_info=True)
            return {
                "message": "I encountered an error processing your request. Please try again.",
                "recommendations": [],
                "agentsUsed": [],
                "threadId": thread_id,
                "projectId": project_id,
                "metadata": {"error": str(e)}
            }
