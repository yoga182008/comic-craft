from pathlib import Path
from io import BytesIO
import requests
from fpdf import FPDF
from PIL import Image


def _load_image(image_url: str):
    if image_url.startswith("/generated/"):
        return Path(__file__).resolve().parents[2] / image_url.lstrip("/")
    if image_url.startswith("http"):
        r = requests.get(image_url, timeout=30)
        r.raise_for_status()
        return BytesIO(r.content)
    return None


def save_pdf(title: str, panels: list[dict], output_path: Path) -> Path:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)

    for panel in panels:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, f"Panel {panel['panel_number']}: {panel['title']}", ln=True)

        image_source = _load_image(panel.get("image_url", ""))
        if image_source is not None:
            try:
                if isinstance(image_source, Path) and image_source.suffix.lower() == ".svg":
                    image_source = None
                if image_source is not None:
                    with Image.open(image_source) as img:
                        img = img.convert("RGB")
                        temp_path = output_path.with_suffix(f".panel{panel['panel_number']}.jpg")
                        img.save(temp_path, format="JPEG")
                    pdf.image(str(temp_path), x=10, y=30, w=190)
                    temp_path.unlink(missing_ok=True)
                    pdf.set_y(140)
            except Exception:
                pass

        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(0, 7, panel.get("scene_description", ""))
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 7, panel.get("narration", ""))
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, panel.get("dialogue", ""))

    pdf.output(str(output_path))
    return output_path
