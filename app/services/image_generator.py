import html
import re
from pathlib import Path
from urllib.parse import quote
import requests
from app.config import get_settings


def _safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_")[:60]


def _fallback_svg(panel_number: int, title: str, prompt: str, output: Path) -> str:
    title = html.escape(title)
    short = html.escape(prompt[:180])
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="600">
<rect width="900" height="600" fill="#f7efe1"/>
<rect x="25" y="25" width="850" height="550" rx="18" fill="white" stroke="#171717" stroke-width="8"/>
<circle cx="450" cy="270" r="125" fill="#ffd166" stroke="#171717" stroke-width="7"/>
<circle cx="405" cy="245" r="13" fill="#171717"/>
<circle cx="495" cy="245" r="13" fill="#171717"/>
<path d="M390 315 Q450 355 510 315" fill="none" stroke="#171717" stroke-width="8"/>
<text x="450" y="90" text-anchor="middle" font-family="Arial" font-size="34" font-weight="700">{title}</text>
<text x="450" y="500" text-anchor="middle" font-family="Arial" font-size="18">{short}</text>
<text x="450" y="545" text-anchor="middle" font-family="Arial" font-size="16">ComicCraft fallback illustration — panel {panel_number}</text>
</svg>"""
    output.write_text(svg, encoding="utf-8")
    return f"/generated/{output.name}"


def generate_image(prompt: str, panel_number: int, title: str) -> str:
    settings = get_settings()
    filename = f"panel_{panel_number}_{_safe_name(title) or 'scene'}.png"
    output = settings.generated_dir / filename

    if settings.hf_api_key:
        url = f"https://api-inference.huggingface.co/models/{quote(settings.hf_image_model, safe='')}"
        try:
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {settings.hf_api_key}"},
                json={"inputs": prompt},
                timeout=120,
            )
            response.raise_for_status()
            if "image" in response.headers.get("content-type", ""):
                output.write_bytes(response.content)
                return f"/generated/{filename}"
        except requests.RequestException:
            pass

    if settings.allow_image_fallback:
        return _fallback_svg(panel_number, title, prompt, output.with_suffix(".svg"))
    raise RuntimeError("Image generation failed and fallback is disabled.")
