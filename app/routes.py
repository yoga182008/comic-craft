import uuid
from fastapi import APIRouter, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.models import ComicRequest, ComicResponse, Panel
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.pdf_generator import save_pdf

router = APIRouter()
settings = get_settings()
templates = Jinja2Templates(directory=str(settings.templates_dir))


def build_comic(data: ComicRequest) -> ComicResponse:
    outline = generate_outline(
        data.story_prompt, data.character_name, data.setting,
        data.tone, data.art_style
    )
    story = generate_story(outline, data.character_name, data.tone)
    story_by_panel = {x["panel_number"]: x for x in story}
    panels = []

    for item in outline:
        number = int(item["panel_number"])
        s = story_by_panel.get(number, {})
        image_url = generate_image(item["image_prompt"], number, item["title"])
        panels.append(Panel(
            panel_number=number,
            title=item["title"],
            scene_description=item["scene_description"],
            image_prompt=item["image_prompt"],
            narration=s.get("narration", ""),
            dialogue=s.get("dialogue", ""),
            image_url=image_url,
        ))

    title = f"{data.character_name}'s Comic"
    pdf_name = f"comic_{uuid.uuid4().hex}.pdf"
    pdf_path = settings.generated_dir / pdf_name
    save_pdf(title, [p.model_dump() for p in panels], pdf_path)

    return ComicResponse(title=title, request=data, panels=panels,
                         pdf_url=f"/generated/{pdf_name}")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"title": settings.app_name}
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    comic = build_comic(ComicRequest(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
    ))
    return templates.TemplateResponse(
        request=request, name="comic_preview.html",
        context={"comic": comic}
    )


@router.post("/generate-comic/json", response_model=ComicResponse)
async def generate_json(data: ComicRequest):
    return build_comic(data)


@router.get("/test-image")
async def test_image():
    url = generate_image(
        "comic book hero in a futuristic city, dramatic lighting, no text",
        0, "Test Image"
    )
    return JSONResponse({"status": "ok", "image_url": url})


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, file: str = ""):
    return templates.TemplateResponse(
        request=request, name="export_success.html", context={"file": file}
    )


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "gemini_configured": bool(settings.gemini_api_key),
        "huggingface_configured": bool(settings.hf_api_key),
    }


@router.get("/generated/{filename}")
async def generated_file(filename: str):
    safe = settings.generated_dir / filename
    if not safe.exists() or safe.parent.resolve() != settings.generated_dir.resolve():
        return JSONResponse({"detail": "File not found"}, status_code=404)
    return FileResponse(safe)
