import json
import re
from typing import List
from app.config import get_settings


def _extract_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
    if not match:
        raise ValueError("Gemini did not return JSON.")
    return json.loads(match.group(1))


def generate_outline(story_prompt: str, character_name: str, setting: str,
                     tone: str, art_style: str) -> List[dict]:
    settings = get_settings()
    if not settings.gemini_api_key:
        return _fallback_outline(story_prompt, character_name, setting, tone, art_style)

    from google import genai
    from google.genai import types
    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = f"""
Create a coherent five-panel comic outline.

Story prompt: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return ONLY valid JSON: an array of exactly five objects.
Every object must contain panel_number, title, scene_description, image_prompt.
Image prompts should describe a single comic panel, preserve the same
character identity, and contain no text inside the generated image.
"""
    response = client.models.generate_content(
        model=settings.gemini_flash_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json",
        ),
    )
    data = _extract_json(response.text)
    if not isinstance(data, list) or len(data) != 5:
        raise ValueError("Outline must contain exactly five panels.")
    return data


def _fallback_outline(story_prompt, character_name, setting, tone, art_style):
    beats = [
        ("The Beginning", f"{character_name} discovers an unexpected problem."),
        ("A Strange Clue", f"{character_name} finds a clue connected to the problem."),
        ("The Challenge", f"{character_name} faces the central challenge."),
        ("The Turning Point", f"{character_name} makes a brave choice."),
        ("The New Dawn", f"{character_name} resolves the problem and learns something."),
    ]
    return [
        {
            "panel_number": i + 1,
            "title": title,
            "scene_description": desc + f" The scene takes place in {setting}.",
            "image_prompt": (
                f"{art_style} comic panel, {setting}, main character {character_name}, "
                f"{desc}, expressive cinematic composition, consistent character design, no text"
            ),
        }
        for i, (title, desc) in enumerate(beats)
    ]
