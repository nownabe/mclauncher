"""
RESTful API and index.html for mclauncher.
"""

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from routers import get_server, start_server

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    The index page returns index.html.
    """
    return templates.TemplateResponse("index.html", context={"request": request})


app.include_router(get_server.router, prefix="/api/v1")
app.include_router(start_server.router, prefix="/api/v1")
