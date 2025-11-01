import reflex as rx
from app.state import ChatState, message_bubble
from app.settings import settings_page
from app.states.resume_state import ResumeState


def chat_interface() -> rx.Component:
    """The main chat interface component."""
    return rx.el.div(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Resume Chatbot",
                    class_name="text-2xl font-bold text-white uppercase tracking-wider",
                ),
                rx.el.a(
                    rx.icon("settings", class_name="text-white"),
                    href="/settings",
                    class_name="p-2 hover:bg-red-700 rounded-full transition-colors",
                ),
                class_name="flex justify-between items-center w-full",
            ),
            class_name="bg-[#141414] p-4 shadow-lg w-full z-10 border-b-2 border-red-600",
        ),
        rx.el.div(
            rx.foreach(ChatState.messages, message_bubble),
            class_name="flex-grow p-4 md:p-6 space-y-4 overflow-y-auto",
        ),
        rx.cond(
            ResumeState.is_loading_cms,
            rx.el.div(
                rx.spinner(class_name="text-red-500"),
                rx.el.p("Syncing with CMS...", class_name="text-gray-400 ml-2"),
                class_name="flex items-center justify-center p-4 bg-[#1f1f1f] border-t border-gray-700",
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.input(
                    placeholder="Ask a question...",
                    on_change=ChatState.set_user_input,
                    on_key_down=lambda e: rx.cond(
                        e == "Enter", ChatState.send_message, rx.console_log("")
                    ),
                    class_name="flex-grow bg-gray-700 text-white rounded-full py-3 px-5 text-base focus:outline-none focus:ring-2 focus:ring-red-500 placeholder-gray-400",
                    default_value=ChatState.user_input,
                ),
                rx.el.button(
                    rx.icon("send", class_name="text-white"),
                    on_click=ChatState.send_message,
                    class_name="bg-red-600 rounded-full p-3 ml-3 shadow-md hover:bg-red-700 transition-all duration-300",
                ),
                class_name="flex items-center w-full",
            ),
            class_name="bg-[#141414] p-4 border-t border-gray-800",
        ),
        class_name="flex flex-col h-screen max-w-3xl mx-auto bg-[#141414] shadow-2xl font-['Montserrat']",
    )


def index() -> rx.Component:
    return rx.el.main(chat_interface(), class_name="bg-black")


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, on_load=ResumeState.load_cms_data)
app.add_page(settings_page, route="/settings", on_load=ResumeState.load_cms_data)