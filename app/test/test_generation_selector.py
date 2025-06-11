from app.services.generation_selector import GenerationSelector

selector = GenerationSelector(model_name="gemini")

prompt = "Dime en qué consiste un sistema RAG en IA."
respuesta = selector.generate(prompt)

print(" Respuesta generada:")
print(respuesta)
