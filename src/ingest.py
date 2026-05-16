import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.path_setup import ensure_project_cwd, ensure_project_root

ensure_project_root()

try:
    import tiktoken
except ImportError:
    tiktoken = None  # type: ignore[assignment]


def _token_length(text: str) -> int:
    if tiktoken is None:
        return max(1, len(text) // 4)
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def _load_documents(data_dir: str):
    """Load .txt files; optionally load .pdf via PyMuPDF when available."""
    docs = []
    if not os.path.isdir(data_dir):
        return docs

    txt_loader = DirectoryLoader(data_dir, glob="*.txt", loader_cls=TextLoader)
    docs.extend(txt_loader.load())

    pdf_files = [f for f in os.listdir(data_dir) if f.lower().endswith(".pdf")]
    if pdf_files:
        try:
            from langchain_community.document_loaders import PyMuPDFLoader

            for pdf_name in pdf_files:
                pdf_path = os.path.join(data_dir, pdf_name)
                docs.extend(PyMuPDFLoader(pdf_path).load())
        except Exception as exc:
            print(f"PDF loader skipped for {data_dir}: {exc}")

    return docs


def ingest_data(data_dir: str, index_path: str, embeddings: HuggingFaceEmbeddings) -> None:
    print(f"Ingesting data from {data_dir}...")

    documents = _load_documents(data_dir)

    if not documents:
        print(f"No documents found in {data_dir}")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        length_function=_token_length,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks (~800 tokens each) from {len(documents)} documents.")

    vectorstore = FAISS.from_documents(chunks, embeddings)

    index_dir = Path(index_path)
    index_dir.parent.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(index_dir))
    print(f"Saved FAISS index to {index_path}\n")


if __name__ == "__main__":
    root = ensure_project_cwd()
    print(f"Working directory: {root}")

    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")

    ingest_data("data/contracts", "faiss_index/contracts", embeddings)
    ingest_data("data/case_law", "faiss_index/case_law", embeddings)

    print("Ingestion complete!")
