from app.services.chat import ChatRAG

chat = ChatRAG()

pregunta = "¿Cuál es la función de los centros de llamadas de emergencias sanitarias?"

respuesta = chat.chat(pregunta)

print(" Respuesta generada:")
print(respuesta)
