import reflex as rx
from .data_structures import PersonalInfo, Experience, Education, Skill, Project
from .datocms_service import fetch_datocms_data
import datetime
import logging


class ResumeState(rx.State):
    """Manages all resume-related data."""

    personal_info: PersonalInfo = {
        "name": "John Doe",
        "title": "Software Engineer",
        "email": "john.doe@email.com",
        "phone": "(123) 456-7890",
        "location": "San Francisco, CA",
        "linkedin": "linkedin.com/in/johndoe",
        "github": "github.com/johndoe",
    }
    experience: list[Experience] = [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Solutions Inc.",
            "duration": "Jan 2020 - Present",
            "description": "Lead development of scalable web applications and mentored junior engineers.",
        }
    ]
    education: list[Education] = [
        {
            "degree": "B.S. in Computer Science",
            "institution": "State University",
            "year": "2019",
        }
    ]
    skills: list[Skill] = []
    projects: list[Project] = []
    resume_filename: str | None = None
    is_loading_cms: bool = False
    last_sync_time: str | None = None
    sync_error: str | None = None
    show_skills: bool = False
    show_projects: bool = False

    @rx.event
    def set_personal_info_field(self, field: str, value: str):
        """Dynamically sets a field in the personal_info dictionary."""
        self.personal_info[field] = value

    @rx.event
    def toggle_skills(self):
        """Toggles the visibility of the skills section."""
        self.show_skills = not self.show_skills

    @rx.event
    def toggle_projects(self):
        """Toggles the visibility of the projects section."""
        self.show_projects = not self.show_projects

    @rx.event
    async def handle_resume_upload(self, files: list[rx.UploadFile]):
        """Handles the upload of a resume file."""
        if not files:
            return rx.toast.error("No file selected.")
        file = files[0]
        upload_data = await file.read()
        outfile = rx.get_upload_dir() / file.name
        with outfile.open("wb") as f:
            f.write(upload_data)
        self.resume_filename = file.name
        return rx.toast.success(f"Successfully uploaded {file.name}")

    async def _sync_data(self):
        """Helper function to perform the actual data sync and state updates."""
        async with self:
            self.is_loading_cms = True
            self.sync_error = None
        try:
            cms_data = await fetch_datocms_data()
            async with self:
                self.skills = cms_data.get("skills", [])
                self.projects = cms_data.get("projects", [])
                self.last_sync_time = datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat()
                self.sync_error = None
            return rx.toast.success("Successfully synced with CMS!")
        except Exception as e:
            logging.exception(f"Error syncing with CMS: {e}")
            error_message = f"Failed to sync with CMS: {str(e)}"
            async with self:
                self.sync_error = error_message
            return rx.toast.error(error_message)
        finally:
            async with self:
                self.is_loading_cms = False

    @rx.event(background=True)
    async def load_cms_data(self):
        """Loads data from DatoCMS on initial page load if not already synced."""
        async with self:
            is_synced = self.last_sync_time is not None
        if not is_synced:
            # Await and return the sync result instead of yielding a coroutine result.
            # Reflex expects an awaited return for background events.
            return await self._sync_data()

    @rx.event
    @rx.event(background=True)
    async def manual_sync_cms_data(self):
        """Allows the user to manually trigger a data sync from DatoCMS.

        Run as a background event and await the actual sync coroutine. This
        ensures we run the same workflow as the automatic loader and return
        the toast/result to the client.
        """
        try:
            return await self._sync_data()
        except Exception as e:
            # _sync_data already logs exceptions, but ensure the manual event
            # doesn't raise unhandled exceptions to the framework.
            logging.exception(f"manual_sync_cms_data failed: {e}")
            self.sync_error = f"Manual sync failed: {e}"
            return rx.toast.error(str(e))