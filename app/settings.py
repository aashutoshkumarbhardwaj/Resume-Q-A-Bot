import reflex as rx
from app.states.resume_state import ResumeState


def form_field(
    label: str, placeholder: str, value: rx.Var, on_change: rx.event.EventHandler
) -> rx.Component:
    """A reusable form field component."""
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-gray-300 mb-1"),
        rx.el.input(
            placeholder=placeholder,
            default_value=value,
            on_change=on_change,
            class_name="w-full bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-red-500 focus:border-red-500 p-2.5 transition placeholder-gray-400",
        ),
        class_name="mb-4",
    )


def personal_info_form() -> rx.Component:
    """Form for editing personal information."""
    return rx.el.div(
        rx.el.h2(
            "Personal Information", class_name="text-xl font-semibold mb-4 text-white"
        ),
        form_field(
            "Name",
            "Your full name",
            ResumeState.personal_info["name"],
            lambda val: ResumeState.set_personal_info_field("name", val),
        ),
        form_field(
            "Title",
            "Your professional title",
            ResumeState.personal_info["title"],
            lambda val: ResumeState.set_personal_info_field("title", val),
        ),
        form_field(
            "Email",
            "your.email@example.com",
            ResumeState.personal_info["email"],
            lambda val: ResumeState.set_personal_info_field("email", val),
        ),
        form_field(
            "Phone",
            "(123) 456-7890",
            ResumeState.personal_info["phone"],
            lambda val: ResumeState.set_personal_info_field("phone", val),
        ),
        form_field(
            "Location",
            "City, State",
            ResumeState.personal_info["location"],
            lambda val: ResumeState.set_personal_info_field("location", val),
        ),
        form_field(
            "LinkedIn",
            "linkedin.com/in/username",
            ResumeState.personal_info["linkedin"],
            lambda val: ResumeState.set_personal_info_field("linkedin", val),
        ),
        form_field(
            "GitHub",
            "github.com/username",
            ResumeState.personal_info["github"],
            lambda val: ResumeState.set_personal_info_field("github", val),
        ),
    )


def resume_upload_section() -> rx.Component:
    """Component for uploading a resume."""
    return rx.el.div(
        rx.el.h2("Upload Resume", class_name="text-xl font-semibold mb-4 text-white"),
        rx.upload.root(
            rx.el.div(
                rx.icon("cloud_upload", class_name="w-12 h-12 mx-auto text-gray-500"),
                rx.el.p(
                    "Drag & drop your resume here, or click to select a file",
                    class_name="text-center text-sm text-gray-400 mt-2",
                ),
                class_name="p-8 border-2 border-dashed border-gray-600 rounded-lg hover:bg-gray-800 transition-colors cursor-pointer",
            ),
            id="resume-upload",
            multiple=False,
            accept={"application/pdf": [".pdf"], "text/plain": [".txt"]},
        ),
        rx.el.div(
            rx.foreach(
                rx.selected_files("resume-upload"),
                lambda file: rx.el.div(
                    rx.icon("file-text", class_name="inline-block mr-2 text-gray-300"),
                    file,
                    class_name="text-sm text-gray-200 bg-gray-700 p-2 rounded-md",
                ),
            ),
            class_name="mt-4 space-y-2",
        ),
        rx.el.button(
            "Upload Resume",
            on_click=ResumeState.handle_resume_upload(
                rx.upload_files(upload_id="resume-upload")
            ),
            class_name="mt-4 w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors shadow-sm",
        ),
        rx.cond(
            ResumeState.resume_filename,
            rx.el.div(
                "Current resume: ",
                rx.el.span(ResumeState.resume_filename, class_name="font-semibold"),
                class_name="mt-4 text-sm text-green-200 bg-green-900/50 p-3 rounded-lg",
            ),
        ),
    )


def cms_sync_section() -> rx.Component:
    """Component for managing sync with DatoCMS."""
    return rx.el.div(
        rx.el.h2("CMS Data Sync", class_name="text-xl font-semibold mb-4 text-white"),
        rx.el.div(
            rx.el.button(
                rx.cond(
                    ResumeState.is_loading_cms,
                    rx.spinner(class_name="mr-2"),
                    rx.icon("refresh-cw", class_name="mr-2 h-4 w-4"),
                ),
                rx.cond(ResumeState.is_loading_cms, "Syncing...", "Sync from CMS"),
                on_click=ResumeState.manual_sync_cms_data,
                disabled=ResumeState.is_loading_cms,
                class_name="flex items-center justify-center w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors shadow-sm disabled:bg-red-800 disabled:cursor-not-allowed",
            ),
            rx.cond(
                ResumeState.last_sync_time,
                rx.el.p(
                    "Last sync: ",
                    rx.moment(ResumeState.last_sync_time, from_now=True),
                    class_name="text-sm text-gray-400 mt-2 text-center",
                ),
            ),
            rx.cond(
                ResumeState.sync_error,
                rx.el.p(
                    ResumeState.sync_error,
                    class_name="text-sm text-red-400 bg-red-900/50 p-2 rounded-md mt-2 text-center",
                ),
            ),
            class_name="p-4 border border-gray-700 rounded-lg bg-gray-800/50",
        ),
    )


def skills_display_section() -> rx.Component:
    """Displays skills fetched from the CMS."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2("Skills", class_name="text-xl font-semibold text-white"),
            rx.el.button(
                rx.icon(rx.cond(ResumeState.show_skills, "chevron-up", "chevron-down")),
                on_click=ResumeState.toggle_skills,
                class_name="text-gray-400 hover:bg-gray-700 p-2 rounded-full",
            ),
            class_name="flex justify-between items-center cursor-pointer",
            on_click=ResumeState.toggle_skills,
        ),
        rx.cond(
            ResumeState.show_skills,
            rx.el.div(
                rx.foreach(
                    ResumeState.skills,
                    lambda skill: rx.el.div(
                        rx.el.h3(
                            skill["category"],
                            class_name="font-semibold text-md text-gray-300 mb-2 mt-4",
                        ),
                        rx.el.div(
                            rx.foreach(
                                skill["technologies"],
                                lambda tech: rx.el.span(
                                    tech,
                                    class_name="bg-gray-700 text-gray-200 text-xs font-medium mr-2 mb-2 px-2.5 py-1 rounded-full",
                                ),
                            ),
                            class_name="flex flex-wrap",
                        ),
                        class_name="mb-4",
                    ),
                ),
                class_name="mt-4 border-t border-gray-700 pt-4",
            ),
        ),
    )


def projects_display_section() -> rx.Component:
    """Displays projects fetched from the CMS."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2("Projects", class_name="text-xl font-semibold text-white"),
            rx.el.button(
                rx.icon(
                    rx.cond(ResumeState.show_projects, "chevron-up", "chevron-down")
                ),
                on_click=ResumeState.toggle_projects,
                class_name="text-gray-400 hover:bg-gray-700 p-2 rounded-full",
            ),
            class_name="flex justify-between items-center cursor-pointer",
            on_click=ResumeState.toggle_projects,
        ),
        rx.cond(
            ResumeState.show_projects,
            rx.el.div(
                rx.foreach(
                    ResumeState.projects,
                    lambda project: rx.el.div(
                        rx.image(
                            src=project["image_url"],
                            fallback="/placeholder.svg",
                            class_name="w-full h-40 object-cover rounded-t-lg",
                        ),
                        rx.el.div(
                            rx.el.h3(
                                project["title"],
                                class_name="font-bold text-lg text-white",
                            ),
                            rx.el.p(
                                project["description"],
                                class_name="text-sm text-gray-400 mt-1 mb-3",
                            ),
                            rx.el.div(
                                rx.foreach(
                                    project["technologies"],
                                    lambda tech: rx.el.span(
                                        tech,
                                        class_name="bg-gray-700 text-gray-200 text-xs font-medium mr-2 mb-2 px-2.5 py-1 rounded-full",
                                    ),
                                ),
                                class_name="flex flex-wrap",
                            ),
                            class_name="p-4",
                        ),
                        class_name="border border-gray-700 rounded-lg shadow-sm overflow-hidden bg-gray-800",
                    ),
                ),
                class_name="mt-4 grid md:grid-cols-2 gap-6 border-t border-gray-700 pt-4",
            ),
        ),
    )


def settings_page() -> rx.Component:
    """The main settings page for managing resume data."""
    return rx.el.main(
        rx.el.div(
            rx.el.header(
                rx.el.div(
                    rx.el.a(
                        rx.icon("arrow-left", class_name="text-white"),
                        href="/",
                        class_name="p-2 hover:bg-red-700 rounded-full transition-colors",
                    ),
                    rx.el.h1(
                        "Settings",
                        class_name="text-2xl font-bold text-white uppercase tracking-wider",
                    ),
                    rx.el.div(class_name="w-8"),
                    class_name="flex items-center justify-between w-full",
                ),
                class_name="bg-[#141414] p-4 shadow-lg w-full z-10 border-b-2 border-red-600",
            ),
            rx.el.div(
                cms_sync_section(),
                skills_display_section(),
                projects_display_section(),
                personal_info_form(),
                resume_upload_section(),
                class_name="p-4 md:p-6 space-y-8",
            ),
            class_name="max-w-3xl mx-auto bg-[#141414] shadow-2xl h-screen font-['Montserrat'] overflow-y-auto",
        ),
        class_name="bg-black",
    )