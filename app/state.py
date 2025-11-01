import reflex as rx
from typing import TypedDict
from app.ai import get_ai_response
from app.states.resume_state import ResumeState


class Message(TypedDict):
    role: str
    content: str


class ChatState(rx.State):
    """Manages the chat messages and user input."""

    messages: list[Message] = [
        {
            "role": "assistant",
            "content": "Hello! I am your personal resume assistant. How can I help you today?",
        }
    ]
    user_input: str = ""

    @rx.event
    def send_message(self):
        """Adds the user's message to the chat and gets a response."""
        if not self.user_input.strip():
            return
        self.messages.append({"role": "user", "content": self.user_input})
        question = self.user_input
        self.user_input = ""
        yield
        self.messages.append({"role": "assistant", "content": "..."})
        yield
        return ChatState.get_response(question)

    @rx.event
    async def get_response(self, question: str):
        resume_state = await self.get_state(ResumeState)
        response_text = await get_ai_response(question, resume_state)
        self.messages[-1] = {"role": "assistant", "content": response_text}


def message_bubble(message: Message) -> rx.Component:
    """Creates a message bubble component for a single message."""
    is_user = message["role"] == "user"
    return rx.el.div(
        rx.el.p(message["content"], class_name="text-base font-medium"),
        class_name=rx.cond(
            is_user,
            "bg-red-600 text-white self-end rounded-t-2xl rounded-bl-2xl shadow-md",
            "bg-gray-700 text-white self-start rounded-t-2xl rounded-br-2xl shadow",
        ),
        style={"padding": "12px 16px", "max_width": "75%"},
    )