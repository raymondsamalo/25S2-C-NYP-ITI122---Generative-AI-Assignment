from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from app.dependencies import DATA_PATH


embeddings = OllamaEmbeddings(model="tinyllama")
vectordb = Chroma(persist_directory=f"{DATA_PATH}/policy_db", 
                  embedding_function=embeddings)
question = "What are overall risk policy ?"

results = vectordb.similarity_search(question, k=3)
print(len(results))
print(results)

