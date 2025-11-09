"""Thread summarization functionality."""

import logging
from typing import List, Optional
import tiktoken
from emergentintegrations.llm.chat import LlmChat, UserMessage
from config import config
from .models import Message, Summary

logger = logging.getLogger(__name__)


class ThreadSummarizer:
    """Summarizes thread conversations when token limits are reached."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.llm.api_key
        self.model = model or config.llm.default_model
        self.provider = config.llm.default_provider
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            return len(text.split())  # Fallback to word count
    
    def count_messages_tokens(self, messages: List[Message]) -> int:
        """Count total tokens in a list of messages."""
        total = 0
        for msg in messages:
            total += self.count_tokens(msg.content)
            # Add tokens for tool calls
            for tool_call in msg.tool_calls:
                total += self.count_tokens(str(tool_call.arguments))
                if tool_call.result:
                    total += self.count_tokens(str(tool_call.result))
        return total
    
    def should_summarize(self, messages: List[Message]) -> bool:
        """Check if thread should be summarized."""
        total_tokens = self.count_messages_tokens(messages)
        return total_tokens >= config.thread.summarization_threshold
    
    async def summarize_messages(
        self,
        messages: List[Message],
        thread_id: str,
        context: Optional[str] = None
    ) -> Summary:
        """Summarize a list of messages."""
        try:
            # Prepare conversation text
            conversation_text = self._format_messages_for_summary(messages)
            
            # Create summarization prompt
            system_message = (
                "You are a helpful assistant that creates concise, informative summaries "
                "of conversations. Focus on key topics, decisions, and important information. "
                "Maintain context about user preferences and requirements."
            )
            
            user_prompt = f"""Please summarize the following conversation:

{conversation_text}

Provide a comprehensive but concise summary that captures:
1. Main topics discussed
2. User preferences or requirements mentioned
3. Key decisions or conclusions
4. Any pending actions or follow-ups
"""
            
            if context:
                user_prompt = f"Previous context: {context}\n\n{user_prompt}"
            
            # Generate summary using LLM
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"summary_{thread_id}",
                system_message=system_message
            ).with_model(self.provider, self.model)
            
            response = await chat.send_message(UserMessage(text=user_prompt))
            summary_text = response.get('content', '')
            
            # Create summary object
            summary = Summary(
                thread_id=thread_id,
                summary_text=summary_text,
                message_count=len(messages),
                token_count=self.count_messages_tokens(messages),
                start_message_id=messages[0].id,
                end_message_id=messages[-1].id
            )
            
            logger.info(f"Created summary for thread {thread_id} covering {len(messages)} messages")
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing messages: {e}")
            # Create a fallback simple summary
            return Summary(
                thread_id=thread_id,
                summary_text=f"Conversation with {len(messages)} messages",
                message_count=len(messages),
                token_count=self.count_messages_tokens(messages),
                start_message_id=messages[0].id,
                end_message_id=messages[-1].id
            )
    
    def _format_messages_for_summary(self, messages: List[Message]) -> str:
        """Format messages for summarization."""
        formatted = []
        for msg in messages:
            role = msg.role.value.upper()
            formatted.append(f"{role}: {msg.content}")
            
            # Include tool call information
            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    formatted.append(f"  [Tool: {tool_call.name}]")
                    if tool_call.result:
                        result_str = str(tool_call.result)[:200]  # Limit length
                        formatted.append(f"  [Result: {result_str}]")
        
        return "\n".join(formatted)
    
    async def get_context_with_summaries(
        self,
        summaries: List[Summary],
        recent_messages: List[Message]
    ) -> str:
        """Build context from summaries and recent messages."""
        context_parts = []
        
        # Add summaries
        if summaries:
            context_parts.append("Previous conversation summary:")
            for summary in summaries:
                context_parts.append(f"- {summary.summary_text}")
            context_parts.append("")
        
        # Add recent messages
        if recent_messages:
            context_parts.append("Recent messages:")
            context_parts.append(self._format_messages_for_summary(recent_messages))
        
        return "\n".join(context_parts)
