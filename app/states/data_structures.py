import reflex as rx
from typing import TypedDict


class PersonalInfo(TypedDict):
    name: str
    title: str
    email: str
    phone: str
    location: str
    linkedin: str
    github: str


class Experience(TypedDict):
    title: str
    company: str
    duration: str
    description: str


class Education(TypedDict):
    degree: str
    institution: str
    year: str


class Skill(TypedDict):
    category: str
    technologies: list[str]


class Project(TypedDict):
    title: str
    description: str
    technologies: list[str]
    achievements: list[str]
    image_url: str | None