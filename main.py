"""
RESTful API and index.html for mclauncher.
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def index():
    """
    The index page returns index.html.
    """
    return {"message": "hello world"}
