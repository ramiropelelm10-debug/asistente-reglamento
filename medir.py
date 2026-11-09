import time

t0 = time.time()
from rag import db, llm, PROMPT, _texto

print(f"1) Carga inicial:        {time.time() - t0:.1f} s")

pregunta = "¿Es obligatorio usar el uniforme?"

t = time.time()
docs = db.similarity_search(pregunta, k=5)
print(f"2) Búsqueda (embedding): {time.time() - t:.1f} s")

contexto = "\n\n".join(d.page_content for d in docs)
t = time.time()
respuesta = llm.invoke(PROMPT.format(contexto=contexto, pregunta=pregunta))
print(f"3) Respuesta de Gemini:  {time.time() - t:.1f} s")
print("\nModelo:", llm.model)
print(_texto(respuesta.content)[:200])