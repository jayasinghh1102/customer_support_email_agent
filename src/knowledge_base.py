import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)

from .config import KNOWLEDGE_BASE_DIR

# This is a global variable to hold the vectorstore so we don't have to rebuild it every time.
vectorstore = None

def get_knowledge_base():
    """
    Initializing the knowledge base if it hasn't been already, then returning it.
    Prevents re-creating the vectorstore on every call.
    """
    global vectorstore
    if vectorstore is not None:
        print("Returning existing knowledge base.")
        return vectorstore

    print("Setting up the knowledge base for the first time...")

    # Load documents from the knowledge base directory
    loaders = []
    for fn in os.listdir(KNOWLEDGE_BASE_DIR):
        path = os.path.join(KNOWLEDGE_BASE_DIR, fn)
        if fn.endswith(".txt"):
            loaders.append(TextLoader(path))
        elif fn.endswith(".pdf"):
            loaders.append(PyPDFLoader(path))

    documents = []
    for loader in loaders:
        documents.extend(loader.load())

    # Split documents into smaller chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    # Create embeddings
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create the Chroma vector store
    vectorstore = Chroma.from_documents(docs, embedding_function)

    print("Knowledge base setup complete.")
    return vectorstore

