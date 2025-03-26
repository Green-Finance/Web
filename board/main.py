from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from router.board import router as board_router
from router.users import router as user_router


app = FastAPI()

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Custom-Header"],
)

app.include_router(user_router)
app.include_router(board_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)