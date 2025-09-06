from fastapi import FastAPI

from .api.routes import api_router

app = FastAPI()

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Swoosh FastAPI application!"}


if __name__ == "__main__":
    import uvicorn
    import os
    from .core.config import *
    from .core.logger import add_file_handler

    add_file_handler(os.path.join(LOG_PATH(), "swoosh.log"))
    uvicorn.run(app, host="0.0.0.0", port=PORT())
