from langchain.schema import Document
from typing import Optional, List
from langchain.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM  # 변경
from langchain import hub
from langchain_core.runnables import RunnablePassthrough


class VectorStoreManager:
    _instance: Optional["VectorStoreManager"] = None
    _vector_store: Optional[FAISS] = None

    @classmethod
    def get_instance(cls) -> "VectorStoreManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_vector_store(self) -> FAISS:
        if self._vector_store is None:
            embeddings = OllamaEmbeddings(
                model="llama3.2:1b", base_url="http://ollama:11434"
            )
            empty_doc = Document(page_content="")
            self._vector_store = FAISS.from_documents(
                documents=[empty_doc], embedding=embeddings
            )
        return self._vector_store

    def add_documents(self, content: str):
        # 문자열을 Document 객체로 변환
        doc = Document(page_content=content)
        vector_store = self.get_vector_store()
        vector_store.add_documents([doc])  # 리스트로 감싸서 전달

    def search_similar_contents(self, query: str) -> str:
        # 유사한 문서 검색
        retriever = self._vector_store.as_retriever()

        llm = OllamaLLM(model="llama3.2:1b", base_url="http://ollama:11434")

        prompt = hub.pull("rlm/rag-prompt")

        def format_docs(docs):
            # 검색한 문서 결과를 하나의 문단으로 합쳐줍니다.
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        response = rag_chain.invoke(query)
        return response

    def clear_store_data(self):
        self._vector_store = None
        self.get_vector_store()
