"""Sub app for api"""

from fastapi import FastAPI

from . import schema


app = FastAPI(root_path="/api/v1")


@app.get("/server", response_model=schema.GetServerResponse)
async def get_server():
    """
    Returns the server status.
    """
    return schema.GetServerResponse(running=False, players=[])


@app.post("/server/start", response_model=schema.StartServerResponse)
def start_server():
    """
    Start the server.
    """
    return {"ok": False}
