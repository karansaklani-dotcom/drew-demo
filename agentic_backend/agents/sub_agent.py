"""Sub-agent implementation with subthreads and subcheckpointing."""

import logging
from typing import Optional, Dict, Any, List
from langchain_core.tools import BaseTool

from .base_agent import BaseAgent
from threads.manager import ThreadManager
from threads.models import MessageType

logger = logging.getLogger(__name__)


class SubAgent(BaseAgent):
    """Sub-agent that operates within a parent agent's context."""
    
    def __init__(
        self,
        agent_type: str,
        parent_thread_id: str,
        system_message: Optional[str] = None,
        tools: Optional[List[BaseTool]] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None
    ):
        super().__init__(
            agent_type=agent_type,
            system_message=system_message,
            tools=tools,
            api_key=api_key,
            model=model,
            provider=provider
        )
        
        self.parent_thread_id = parent_thread_id
        self.subthread_id: Optional[str] = None
    
    async def initialize(self):
        """Initialize the sub-agent and create subthread."""
        try:
            # Call parent initialization
            await super().initialize()
            
            # Create a subthread
            subthread = await self.thread_manager.create_thread(
                agent_type=self.agent_type,
                parent_thread_id=self.parent_thread_id,
                title=f"Subthread for {self.agent_type}",
                metadata={
                    "is_subagent": True,
                    "parent_thread": self.parent_thread_id
                }
            )
            
            self.subthread_id = subthread.id
            logger.info(f"Sub-agent initialized with subthread {self.subthread_id}")
            
        except Exception as e:
            logger.error(f"Error initializing sub-agent: {e}")
            raise
    
    async def execute_subtask(
        self,
        task_description: str,
        parent_message_id: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a subtask within the subthread."""
        try:
            if not self.subthread_id:
                raise ValueError("Sub-agent not properly initialized")
            
            logger.info(f"Executing subtask in subthread {self.subthread_id}")
            
            # Build message with context
            message = task_description
            if context:
                message = f"Context from parent: {context}\n\nTask: {task_description}"
            
            # Invoke the sub-agent
            result = await self.invoke(
                message=message,
                thread_id=self.subthread_id
            )
            
            # Link the response to parent message if provided
            if parent_message_id and result.get('response'):
                await self.thread_manager.add_message(
                    thread_id=self.parent_thread_id,
                    role=MessageType.ASSISTANT,
                    content=f"[Sub-agent {self.agent_type}]: {result['response']}",
                    parent_message_id=parent_message_id,
                    metadata={
                        "is_subagent_response": True,
                        "subagent_type": self.agent_type,
                        "subthread_id": self.subthread_id
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing subtask: {e}")
            return {
                "error": str(e),
                "subthread_id": self.subthread_id
            }
    
    async def get_subthread_history(self) -> List[Dict[str, Any]]:
        """Get the history of the subthread."""
        try:
            if not self.subthread_id:
                return []
            
            messages = await self.thread_manager.get_messages(self.subthread_id)
            return [msg.dict() for msg in messages]
            
        except Exception as e:
            logger.error(f"Error getting subthread history: {e}")
            return []
    
    async def merge_context_to_parent(
        self,
        summary: Optional[str] = None
    ) -> bool:
        """Merge subthread context back to parent thread."""
        try:
            if not self.subthread_id:
                return False
            
            # Get subthread messages
            messages = await self.thread_manager.get_messages(self.subthread_id)
            
            # Create summary if not provided
            if not summary and messages:
                summary_obj = await self.thread_manager.summarizer.summarize_messages(
                    messages,
                    self.subthread_id,
                    context=f"Subtask completed by {self.agent_type}"
                )
                summary = summary_obj.summary_text
            
            # Add summary to parent thread
            if summary:
                await self.thread_manager.add_message(
                    thread_id=self.parent_thread_id,
                    role=MessageType.SYSTEM,
                    content=f"[Sub-agent {self.agent_type} completed]: {summary}",
                    metadata={
                        "is_subagent_summary": True,
                        "subagent_type": self.agent_type,
                        "subthread_id": self.subthread_id
                    },
                    generate_embedding=False
                )
            
            logger.info(f"Merged subthread {self.subthread_id} context to parent {self.parent_thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error merging context to parent: {e}")
            return False


async def create_sub_agent(
    agent_type: str,
    parent_thread_id: str,
    system_message: Optional[str] = None,
    tools: Optional[List[BaseTool]] = None
) -> SubAgent:
    """Factory function to create and initialize a sub-agent."""
    sub_agent = SubAgent(
        agent_type=agent_type,
        parent_thread_id=parent_thread_id,
        system_message=system_message,
        tools=tools
    )
    
    await sub_agent.initialize()
    return sub_agent
