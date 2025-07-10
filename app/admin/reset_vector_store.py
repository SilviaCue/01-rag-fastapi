from app.services.vector_store import VectorStore

def reset_vector_store():
    vs = VectorStore(embedding_model="huggingface")
    vs.reset()
    print("Vector store reseteado correctamente.")

if __name__ == "__main__":
    reset_vector_store()

# ===============================================================
# Scripts de administración (app/admin/)
#
# Esta carpeta contiene utilidades internas para tareas administrativas
# y de mantenimiento del sistema.
#
# reset_vector_store.py
# Script para resetear (vaciar) el índice de vectores FAISS.
# Úsalo solo si quieres borrar todo el conocimiento indexado
# y empezar de cero.
#
# Ejemplo de uso desde la terminal:
#   python -m app.admin.reset_vector_store
#
# NOTA: No es necesario para el uso habitual de la API.
#       Solo para mantenimiento o desarrollo.
# ===============================================================


