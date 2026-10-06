# ComicCraft — AI Comic Story Creator

A FastAPI + Jinja2 application that turns a story prompt into a five-panel comic.

## Workflow
1. Gemini generates a structured five-panel outline.
2. Gemini generates narration and dialogue.
3. Hugging Face Stable Diffusion generates illustrations.
4. The backend builds the comic layout.
5. A PDF is generated for download.

## Structure
```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_flash.py
│   │   ├── gemini_pro.py
│   │   ├── image_generator.py
│   │   └── pdf_generator.py
│   ├── static/css/style.css
│   ├── static/js/app.js
│   └── templates/
│       ├── index.html
│       ├── comic_preview.html
│       └── export_success.html
├── tests/test_app.py
├── generated/.gitkeep
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Windows setup
```powershell
python -m venv env
env\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Put your API keys in `.env`.

## Run
```powershell
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 and http://127.0.0.1:8000/docs

## Test
```powershell
pytest -q
```

The test suite does not require paid AI calls.
