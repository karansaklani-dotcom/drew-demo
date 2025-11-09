"""
LangGraph-based Recommendation Agent for Drew
Handles user prompts and provides activity recommendations
"""
import os
import uuid
from typing import List, Dict, Any, Optional, TypedDict, Annotated
from datetime import datetime
import logging

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import operator

from semantic_search import SemanticSearchService

logger = logging.getLogger(__name__)

# ============================================================================
# STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """State for the recommendation agent"""
    messages: Annotated[List, operator.add]
    user_prompt: str
    user_id: Optional[str]
    session_id: str
    
    # Extracted intent
    intent: Optional[str]
    
    # Search parameters
    search_query: str
    filters: Dict[str, Any]
    
    # Results
    search_results: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    
    # Response
    response_message: str
    suggested_questions: List[str]
    
    # Metadata
    metadata: Dict[str, Any]

# ============================================================================
# RECOMMENDATION AGENT
# ============================================================================

class RecommendationAgent:
    """
    LangGraph agent for activity recommendations based on user prompts
    """
    
    def __init__(
        self,
        openai_api_key: str,
        semantic_search_service: SemanticSearchService,
        model_name: str = "gpt-4o-mini"
    ):
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model=model_name,
            temperature=0.7
        )
        self.semantic_search = semantic_search_service
        self.checkpointer = MemorySaver()
        
        # Build the graph
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("understand_intent", self.understand_intent)
        workflow.add_node("extract_filters", self.extract_filters)
        workflow.add_node("search_activities", self.search_activities)
        workflow.add_node("rank_results", self.rank_results)
        workflow.add_node("generate_response", self.generate_response)
        
        # Define edges
        workflow.set_entry_point("understand_intent")
        workflow.add_edge("understand_intent", "extract_filters")
        workflow.add_edge("extract_filters", "search_activities")
        workflow.add_edge("search_activities", "rank_results")
        workflow.add_edge("rank_results", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def understand_intent(self, state: AgentState) -> AgentState:
        """Understand user intent from prompt"""
        logger.info("Understanding user intent")
        
        system_prompt = """You are a helpful assistant that understands user requests for activities and events.
        
Your job is to:
1. Identify the user's intent (search, recommend, browse, ask question)
2. Extract key information like location, occasion, group size, interests, etc.
3. Create a concise search query

Respond in this format:
INTENT: <intent_type>
SEARCH_QUERY: <optimized search query>
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["user_prompt"])
        ]
        
        response = await self.llm.ainvoke(messages)
        content = response.content
        
        # Parse response
        intent = "recommend"  # default
        search_query = state["user_prompt"]
        
        for line in content.split("\n"):
            if line.startswith("INTENT:"):
                intent = line.split("INTENT:")[1].strip().lower()
            elif line.startswith("SEARCH_QUERY:"):
                search_query = line.split("SEARCH_QUERY:")[1].strip()
        
        state["intent"] = intent
        state["search_query"] = search_query
        state["messages"].append(HumanMessage(content=state["user_prompt"]))
        
        logger.info(f"Intent: {intent}, Search query: {search_query}")
        return state
    
    async def extract_filters(self, state: AgentState) -> AgentState:
        """Extract filters from user prompt"""
        logger.info("Extracting filters")
        
        system_prompt = """Extract structured filters from the user's request.

Available filters:
- location: city or state
- category: type of activity
- minParticipants/maxParticipants: group size
- minDuration/maxDuration: duration in minutes
- priceMin/priceMax: price range
- occasion: special occasion

Respond in this format (one per line, omit if not mentioned):
LOCATION: <city, state>
CATEGORY: <category>
PARTICIPANTS: <min>-<max>
DURATION: <min>-<max> (in minutes)
PRICE: <min>-<max>
OCCASION: <occasion>
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["user_prompt"])
        ]
        
        response = await self.llm.ainvoke(messages)
        content = response.content
        
        filters = {}
        
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("LOCATION:"):
                location = line.split("LOCATION:")[1].strip()
                # Could be "San Francisco, CA" or just "San Francisco"
                parts = [p.strip() for p in location.split(",")]
                if len(parts) >= 1:
                    filters["city"] = {"$regex": parts[0], "$options": "i"}
                if len(parts) >= 2:
                    filters["state"] = {"$regex": parts[1], "$options": "i"}
            
            elif line.startswith("CATEGORY:"):
                category = line.split("CATEGORY:")[1].strip()
                filters["category"] = {"$regex": category, "$options": "i"}
            
            elif line.startswith("PARTICIPANTS:"):
                parts = line.split("PARTICIPANTS:")[1].strip()
                if "-" in parts:
                    min_p, max_p = parts.split("-")
                    try:
                        filters["maxParticipants"] = {"$gte": int(min_p.strip())}
                        filters["minParticipants"] = {"$lte": int(max_p.strip())}
                    except ValueError:
                        pass
            
            elif line.startswith("DURATION:"):
                parts = line.split("DURATION:")[1].strip()
                if "-" in parts:
                    min_d, max_d = parts.split("-")
                    try:
                        filters["maxDuration"] = {"$gte": int(min_d.strip())}
                        filters["minDuration"] = {"$lte": int(max_d.strip())}
                    except ValueError:
                        pass
            
            elif line.startswith("PRICE:"):
                parts = line.split("PRICE:")[1].strip()
                if "-" in parts:
                    min_price, max_price = parts.split("-")
                    try:
                        filters["price"] = {
                            "$gte": float(min_price.strip()),
                            "$lte": float(max_price.strip())
                        }
                    except ValueError:
                        pass
        
        state["filters"] = filters
        logger.info(f"Extracted filters: {filters}")
        return state
    
    async def search_activities(self, state: AgentState) -> AgentState:
        """Search for activities using semantic search"""
        logger.info("Searching activities")
        
        results = await self.semantic_search.semantic_search_activities(
            query=state["search_query"],
            limit=10,
            filters=state["filters"] if state["filters"] else None
        )
        
        state["search_results"] = results
        logger.info(f"Found {len(results)} results")
        return state
    
    async def rank_results(self, state: AgentState) -> AgentState:
        """Rank and score results based on relevance"""
        logger.info("Ranking results")
        
        if not state["search_results"]:
            state["recommendations"] = []
            return state
        
        # Use LLM to rank and explain matches
        system_prompt = """You are an expert at matching activities to user preferences.

Given the user's request and a list of activities, rank them and explain why each is a good match.

For each activity, provide:
1. A relevance score (0-1)
2. A brief reasoning (1-2 sentences)
3. Key matching criteria

Format your response as:
ACTIVITY: <activity_id>
SCORE: <0.XX>
REASONING: <explanation>
CRITERIA: <criterion1>, <criterion2>, ...
---
"""
        
        # Prepare activities summary for LLM
        activities_summary = []
        for idx, activity in enumerate(state["search_results"][:5]):  # Top 5
            summary = f"""
Activity {idx + 1} (ID: {activity.get('_id')}):
- Title: {activity.get('title')}
- Description: {activity.get('shortDescription', '')}
- Location: {activity.get('city', 'N/A')}, {activity.get('state', 'N/A')}
- Category: {activity.get('category', 'N/A')}
- Price: ${activity.get('price', 0)}
- Participants: {activity.get('minParticipants', 0)}-{activity.get('maxParticipants', 0)}
"""
            activities_summary.append(summary)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User request: {state['user_prompt']}\n\nActivities:\n" + "\n".join(activities_summary))
        ]
        
        response = await self.llm.ainvoke(messages)
        content = response.content
        
        # Parse rankings
        recommendations = []
        current = {}
        
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("ACTIVITY:"):
                if current:
                    recommendations.append(current)
                current = {"activityId": line.split("ACTIVITY:")[1].strip()}
            elif line.startswith("SCORE:"):
                try:
                    current["score"] = float(line.split("SCORE:")[1].strip())
                except ValueError:
                    current["score"] = 0.5
            elif line.startswith("REASONING:"):
                current["reasoning"] = line.split("REASONING:")[1].strip()
            elif line.startswith("CRITERIA:"):
                criteria = line.split("CRITERIA:")[1].strip()
                current["matchedCriteria"] = [c.strip() for c in criteria.split(",")]
            elif line == "---" and current:
                recommendations.append(current)
                current = {}
        
        if current:
            recommendations.append(current)
        
        # Match recommendations with full activity data
        for rec in recommendations:
            activity_id = rec["activityId"]
            # Find matching activity
            for activity in state["search_results"]:
                if str(activity.get("_id")) == activity_id:
                    rec["activity"] = activity
                    break
        
        # Sort by score
        recommendations.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        state["recommendations"] = recommendations
        logger.info(f"Ranked {len(recommendations)} recommendations")
        return state
    
    async def generate_response(self, state: AgentState) -> AgentState:
        """Generate final response message"""
        logger.info("Generating response")
        
        if not state["recommendations"]:
            state["response_message"] = "I couldn't find any activities matching your request. Could you provide more details about what you're looking for?"
            state["suggested_questions"] = [
                "What location are you interested in?",
                "What type of activity are you looking for?",
                "How many people will be participating?"
            ]
            return state
        
        # Generate friendly response
        system_prompt = """You are a friendly activity recommendation assistant.

Given recommendations, create a warm, conversational response that:
1. Acknowledges the user's request
2. Introduces the top recommendations
3. Highlights why they're good matches
4. Encourages engagement

Keep it concise (2-3 sentences) and enthusiastic!
"""
        
        top_recs = state["recommendations"][:3]
        recs_summary = "\n".join([
            f"- {rec.get('activity', {}).get('title', 'Unknown')}: {rec.get('reasoning', '')}"
            for rec in top_recs
        ])
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User asked: {state['user_prompt']}\n\nTop recommendations:\n{recs_summary}")
        ]
        
        response = await self.llm.ainvoke(messages)
        state["response_message"] = response.content
        
        # Generate follow-up questions
        state["suggested_questions"] = [
            "Tell me more about the first recommendation",
            "Do you have activities for a different group size?",
            "What else is available in this area?"
        ]
        
        logger.info("Response generated")
        return state
    
    async def run(
        self,
        prompt: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run the agent with a user prompt"""
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Initialize state
        initial_state: AgentState = {
            "messages": [],
            "user_prompt": prompt,
            "user_id": user_id,
            "session_id": session_id,
            "intent": None,
            "search_query": "",
            "filters": {},
            "search_results": [],
            "recommendations": [],
            "response_message": "",
            "suggested_questions": [],
            "metadata": context or {}
        }
        
        # Run the graph
        config = {"configurable": {"thread_id": session_id}}
        
        try:
            final_state = await self.graph.ainvoke(initial_state, config)
            
            return {
                "message": final_state["response_message"],
                "recommendations": final_state["recommendations"],
                "suggestedQuestions": final_state["suggested_questions"],
                "sessionId": session_id,
                "metadata": {
                    "intent": final_state.get("intent"),
                    "resultsCount": len(final_state["search_results"]),
                    "recommendationsCount": len(final_state["recommendations"])
                }
            }
        
        except Exception as e:
            logger.error(f"Error running agent: {e}", exc_info=True)
            return {
                "message": "I encountered an error processing your request. Please try again.",
                "recommendations": [],
                "suggestedQuestions": ["Can you rephrase your question?"],
                "sessionId": session_id,
                "metadata": {"error": str(e)}
            }
