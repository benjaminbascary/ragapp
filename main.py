from dotenv import load_dotenv
from src.constants import ENV_FILE_PATH

load_dotenv(
    dotenv_path=ENV_FILE_PATH,
)

import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from create_llama.backend.app.settings import init_settings
from create_llama.backend.app.api.routers.chat import chat_router
from src.routers.management.config import config_router
from src.routers.management.files import files_router
from src.routers.management.tools import tools_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
init_settings()

environment = os.getenv("ENVIRONMENT")
if environment == "dev":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add chat router from create_llama/backend
app.include_router(chat_router, prefix="/api/chat")
app.include_router(config_router, prefix="/api/management/config")
app.include_router(files_router, prefix="/api/management/files")
app.include_router(tools_router, prefix="/api/management/tools")


@app.get("/")
async def redirect():
    from src.models.env_config import get_config

    config = get_config()
    if config.configured:
        # system is configured - / points to chat UI
        return FileResponse("static/index.html")
    else:
        # system is not configured - redirect to onboarding page
        return RedirectResponse(url="/admin/#new")


def mount_static_files(directory, path):
    if os.path.exists(directory):
        app.mount(path, StaticFiles(directory=directory), name=f"{directory}-static")


# Mount the data files to serve the file viewer
mount_static_files("data", "/api/files/data")

# Mount the output files from tools
mount_static_files("tool-output", "/api/files/tool-output")

# Mount the frontend static files
mount_static_files("static", "")

if __name__ == "__main__":
    app_host = os.getenv("APP_HOST", "0.0.0.0")
    app_port = int(os.getenv("APP_PORT", "8000"))
    reload = environment == "dev"

    uvicorn.run(app="main:app", host=app_host, port=app_port, reload=reload)
