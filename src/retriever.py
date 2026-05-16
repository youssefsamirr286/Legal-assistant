import os
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

class LegalRetriever:
    def __init__(self):
        self.embeddings: Optional[HuggingFaceEmbeddings] = None
        self.init_error: Optional[str] = None

        try:
            self.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
        except Exception as exc:
            self.init_error = (
                "Failed to initialize embedding model. "
                "Run dependency setup and check internet access for first model download. "
                f"Details: {exc}"
            )

        # Load indices if they exist
        self.contracts_store = self._load_store("faiss_index/contracts")
        self.case_law_store = self._load_store("faiss_index/case_law")

    def _load_store(self, path):
        if not self.embeddings:
            return None
        if os.path.exists(path):
            # allow_dangerous_deserialization=True is required for loading local FAISS files safely created by us
            try:
                return FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
            except Exception:
                return None
        return None

    def _get_unavailable_reason(self, source_name: str) -> str:
        if self.init_error:
            return self.init_error
        return (
            f"{source_name} database is empty or not initialized. "
            "Run `python src/ingest.py` after adding source .txt files."
        )

    def search_contracts(self, query: str, k: int = 3):
        """Search the contracts vector database for the query."""
        if not self.contracts_store:
            return self._get_unavailable_reason("Contracts")
        
        docs = self.contracts_store.similarity_search(query, k=k)
        return self._format_docs(docs, "Contracts")

    def search_case_law(self, query: str, k: int = 3):
        """Search the case law vector database for the query."""
        if not self.case_law_store:
            return self._get_unavailable_reason("Case law")
        
        docs = self.case_law_store.similarity_search(query, k=k)
        return self._format_docs(docs, "Case Law")

    def search_all_parallel(self, query: str, k: int = 3) -> str:
        """Search contracts and case law vector stores in parallel."""
        with ThreadPoolExecutor(max_workers=2) as pool:
            contracts_future = pool.submit(self.search_contracts, query, k)
            case_law_future = pool.submit(self.search_case_law, query, k)
            return contracts_future.result() + "\n\n" + case_law_future.result()

    def _format_docs(self, docs, source_type: str):
        if not docs:
            return f"No relevant {source_type} found."
            
        formatted = f"--- Retrieved from {source_type} ---\n"
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Unknown")
            formatted += f"[Doc {i+1} | Source: {os.path.basename(source)}]\n{doc.page_content}\n\n"
        return formatted
