from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from app.dependencies import DATA_PATH
# Extract Data From the PDF File
def load_pdf_file(data):
    loader = DirectoryLoader(data, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents

# Split the Data into Text Chunks
def text_split(extracted_data):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)  # size by characters
    text_chunks=text_splitter.split_documents(extracted_data)
    return text_chunks

extracted_data = load_pdf_file(data=DATA_PATH)
# print(type(extracted_data), len(extracted_data))   # Organize by the pages. Total pages: 68.
print(extracted_data)
text_chunks=text_split(extracted_data)
print("Length of Text Chunks", len(text_chunks))

embeddings = OllamaEmbeddings(model="tinyllama")
vectordb = Chroma.from_texts([t.page_content for t in text_chunks],
                             embeddings,
                             collection_name="policy",
                             persist_directory=f"{DATA_PATH}/policy_db")

question = "What are overall risk policy for credit score 455?"
results = vectordb.similarity_search(question, k=3)
print(len(results))
print(results)