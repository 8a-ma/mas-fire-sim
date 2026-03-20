from fastapi import FastAPI, Response


app = FastAPI()

@app.get("/api/v1/health")
def get_health():
    return Response(status_code=204)

