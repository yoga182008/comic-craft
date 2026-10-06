from typing import List
from pydantic import BaseModel, Field


class ComicRequest(BaseModel):
    story_prompt: str = Field(..., min_length=5, max_length=3000)
    character_name: str = Field(..., min_length=1, max_length=100)
    setting: str = Field(..., min_length=1, max_length=100)
    tone: str = Field(..., min_length=1, max_length=100)
    art_style: str = Field(..., min_length=1, max_length=100)


class Panel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    narration: str = ""
    dialogue: str = ""
    image_url: str = ""


class ComicResponse(BaseModel):
    title: str
    request: ComicRequest
    panels: List[Panel]
    pdf_url: str = ""
