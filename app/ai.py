import os
import reflex as rx
import google.generativeai as genai
import logging
from app.states.resume_state import ResumeState


async def get_ai_response(question: str, resume_state: ResumeState) -> str:
    """Get the AI response using Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "GEMINI_API_KEY is not set. Please configure it in your environment."
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        resume_context = _build_resume_context(resume_state)
        prompt = f"You are a helpful AI assistant representing a job candidate. Answer questions based on the candidate's resume.\n        Your tone should be professional, friendly, and confident. Keep your answers concise but informative.\n\n        Here is the candidate's resume information:\n        --- START RESUME ---\n        {resume_context}\n        --- END RESUME ---\n\n        User's question: {question}\n\n        Based on the resume, answer as the candidate would:\n        "
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        logging.exception(f"Error getting AI response: {e}")
        return f"An error occurred with the AI service: {str(e)}"


def _build_resume_context(state: ResumeState) -> str:
    context = """**Experience**
"""
    for exp in state.experience:
        context += f"- **{exp['title']}** at {exp['company']} ({exp['duration']})\n  {exp['description']}\n"
    context += """
"""
    context += """**Education**
"""
    for edu in state.education:
        context += f"- {edu['degree']}, {edu['institution']} ({edu['year']})\n"
    context += """
"""
    context += """**Skills**
"""
    for skill in state.skills:
        techs = ", ".join(skill["technologies"])
        context += f"- **{skill['category']}**: {techs}\n"
    context += """
"""
    context += """**Projects**
"""
    for proj in state.projects:
        techs = ", ".join(proj["technologies"])
        achievements = """
    """.join([f"- {a}" for a in proj["achievements"]])
        context += f"- **{proj['title']}** ({techs})\n  {proj['description']}\n  Achievements:\n    {achievements}\n"
    context += """
"""
    if state.resume_filename:
        context += f"A full resume is also available: {state.resume_filename}\n"
    return context