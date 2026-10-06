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


def generate_story(outline: List[dict], character_name: str, tone: str) -> List[dict]:
    settings = get_settings()
    if not settings.gemini_api_key:
        return _fallback_story(outline, character_name)

    from google import genai
    from google.genai import types
    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = f"""
Write detailed narration and character dialogue for this five-panel comic.

Main character: {character_name}
Tone: {tone}
Outline:
{json.dumps(outline, ensure_ascii=False)}

Return ONLY valid JSON: an array of exactly five objects.
Each object must contain panel_number, narration, dialogue.
Keep narration concise enough for a comic panel.
"""
    response = client.models.generate_content(
        model=settings.gemini_pro_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.85,
            response_mime_type="application/json",
        ),
    )
    data = _extract_json(response.text)
    if not isinstance(data, list) or len(data) != 5:
        raise ValueError("Story response must contain exactly five panels.")
    return data


def _fallback_story(outline, character_name):
    return [
        {
            "panel_number": p["panel_number"],
            "narration": p["scene_description"],
            "dialogue": f'{character_name}: "I have to keep going!"',
        }
        for p in outline
    ]
