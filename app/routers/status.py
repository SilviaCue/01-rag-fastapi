# app/routers/status.py

from fastapi import APIRouter, HTTPException
from app.services.vector_store_singleton import vector_store_instance as vector_store

router = APIRouter()

@router.get("/status/")
def get_index_status():
    """
    Devuelve el número total de chunks indexados actualmente.
    """
    try:
        total_chunks = vector_store.index.ntotal
        return {
            "status": "ok",
            "total_chunks_indexados": total_chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar el estado del índice: {str(e)}")
