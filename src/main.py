from fastapi import FastAPI, Response
from config.settings import Settings


settings = Settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    root_path="/api/v1"
)

@app.get("/health")
def get_health():
    return Response(status_code=204)

