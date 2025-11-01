import os
import reflex as rx
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import logging


async def fetch_datocms_data() -> dict[str, list]:
    """Fetches skills and projects from DatoCMS."""
    api_token = os.getenv("DATOCMS_API_TOKEN")
    # If the token isn't in the environment, try to read a `.env` file in the
    # repository root. Many local dev setups keep secrets in a .env file but do
    # not export them into the process environment; this makes the function
    # more robust during local development.
    if not api_token:
        try:
            from pathlib import Path

            env_path = Path.cwd() / ".env"
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    # Very small parser for KEY=VALUE lines; ignore comments and empty lines
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    if k.strip() == "DATOCMS_API_TOKEN":
                        api_token = v.strip()
                        break
        except Exception:
            logging.exception("Failed to read .env file to obtain DATOCMS_API_TOKEN")

    if not api_token:
        # Don't raise here — returning empty data allows the app to function
        # offline or without CMS configured. The caller will set an error
        # message in state if needed.
        logging.warning("DATOCMS_API_TOKEN not found in environment or .env — skipping CMS sync.")
        return {"skills": [], "projects": []}
    transport = AIOHTTPTransport(
        url="https://graphql.datocms.com/",
        headers={"Authorization": f"Bearer {api_token}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)
    query = gql("""
        query ResumeData {
            allSkills(first: 20, orderBy: _createdAt_ASC) {
                name
                category
            }
            allProjects(first: 8, orderBy: _createdAt_ASC) {
                title
                description
                techUsed
                image {
                    url(imgixParams: {auto: format, w: "500"})
                }
            }
        }
        """)
    try:
        async with client as session:
            result = await session.execute(query)
            raw_skills = result.get("allSkills", [])
            raw_projects = result.get("allProjects", [])
            skills_by_category = {}
            for skill in raw_skills:
                category = skill.get("category", "Other")
                if category not in skills_by_category:
                    skills_by_category[category] = []
                skills_by_category[category].append(skill.get("name"))
            formatted_skills = [
                {"category": cat, "technologies": techs}
                for cat, techs in skills_by_category.items()
            ]
            formatted_projects = [
                {
                    "title": p.get("title", ""),
                    "description": p.get("description", ""),
                    "technologies": [
                        s.strip() for s in p.get("techUsed", "").split(",")
                    ]
                    if p.get("techUsed")
                    else [],
                    "achievements": [],
                    "image_url": p.get("image", {}).get("url")
                    if p.get("image")
                    else None,
                }
                for p in raw_projects
            ]
            return {"skills": formatted_skills, "projects": formatted_projects}
    except Exception as e:
        logging.exception(f"Error fetching from DatoCMS: {e}")
        raise e