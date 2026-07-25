"""
Service for handling chat interactions using LangChain.

This service manages conversational memory and orchestrates the flow of chat messages
between the user and the language model.
"""

from typing import Any, Dict, List, Mapping, Optional

from langchain.chains import ConversationChain
from langchain.llms.base import LLM
from langchain.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate

from app.services.llm_service_protocol import LLMServiceProtocol


class ProtocolLLM(LLM):
    """
    An adapter class that wraps an LLMServiceProtocol implementation to make it
    compatible with LangChain's LLM interface.
    """

    llm_service: LLMServiceProtocol
    system_prompt: str = "You are a helpful assistant."

    @property
    def _llm_type(self) -> str:
        """Return the type of LLM."""
        return "protocol_llm"

    async def _acall(
        self,
        prompt: str,  # This will be the fully formatted prompt from the ConversationChain
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        """
        Asynchronously call the underlying LLM service.
        The 'prompt' from ConversationChain is the full, formatted prompt including history.
        """
        # The `prompt` here is already formatted by the ConversationChain's prompt template.
        # We can pass it directly as the user_prompt to the underlying service.
        response = await self.llm_service.generate_text_from_prompt(
            system_prompt=self.system_prompt,
            user_prompt=prompt,
            input_vars=kwargs.get("input_vars", {}),
        )
        return response

    def _call(
        self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any
    ) -> str:
        """Synchronous call is not supported."""
        raise NotImplementedError("This LLM only supports async calls.")

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters of the LLM."""
        return {"llm_service": self.llm_service.__class__.__name__}


class ChatService:
    """
    Service to manage chat conversations.

    This service uses a dictionary to maintain separate conversation histories
    for different session IDs.
    """

    def __init__(self, llm_service: LLMServiceProtocol):
        self.llm_adapter = ProtocolLLM(llm_service=llm_service)
        self.conversations: Dict[str, ConversationChain] = {}

    def _get_or_create_conversation(self, session_id: str) -> ConversationChain:
        """Retrieve an existing conversation or create a new one for the session_id."""
        if session_id not in self.conversations:
            # Define a prompt template that includes history
            # This template is compatible with ConversationBufferMemory, which formats history with "Human:" and "AI:" prefixes.
            template = """
            The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.

            {history}
            Human: {input}
            AI:"""

            PROMPT = PromptTemplate(
                input_variables=["history", "input"], template=template
            )

            self.conversations[session_id] = ConversationChain(
                llm=self.llm_adapter,
                prompt=PROMPT,
                memory=ConversationBufferMemory(),
                verbose=True,
            )
        return self.conversations[session_id]

    async def get_chat_response(
        self,
        session_id: str,
        user_message: Optional[str] = None,
        ai_message: Optional[str] = None,
    ) -> str:
        """
        Asynchronously gets a chat response from the LLM.

        This method now correctly handles conversation seeding and follow-up messages.
        If only an `ai_message` is provided, it seeds the history. If a `user_message`
        is provided, it generates the next response.
        """
        conversation = self._get_or_create_conversation(session_id)

        # Manually add the previous AI message to the history if it exists.
        if ai_message:
            # To seed the conversation, we need a dummy user message to maintain the turn-based structure.
            # We'll add the AI message to the buffer, but LangChain's memory works best
            # when it saves a full turn (user + ai). A better approach might be to
            # load history directly if the API supports it.
            # For now, we add the AI message directly.
            conversation.memory.chat_memory.add_ai_message(ai_message)

        # If there's no user message, we are just seeding the chat, so we don't generate a response.
        if not user_message:
            return ""

        # Add the user's current message and get a new prediction.
        response = await conversation.apredict(input=user_message)

        return response
