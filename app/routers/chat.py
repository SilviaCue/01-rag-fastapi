from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat import ChatRAG

router = APIRouter()

# Modelo de entrada de la petición
class ChatRequest(BaseModel):
    question: str

# Instancia única de ChatRAG
chat_service = ChatRAG()
# Endpoint para el chat
@router.post("/chat/")
async def chat_endpoint(request: ChatRequest):
    response = chat_service.chat(request.question)
    return {"response": response}