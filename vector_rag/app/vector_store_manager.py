import os
from langchain.schema import Document
from typing import Optional
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import logging
from langchain_ollama import OllamaLLM  # 변경
from langchain_core.prompts import PromptTemplate
from langsmith import Client

logger = logging.getLogger(__name__)


class VectorStoreManager:
    _instance: Optional["VectorStoreManager"] = None
    _vector_store: Optional[FAISS] = None
    _llm = None
    _embeddings = None

    @classmethod
    def get_instance(cls) -> "VectorStoreManager":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._init_models()
        return cls._instance

    def _init_models(self):
        """모델 초기화 (임베딩 및 LLM)"""
        logger.info("Init LLM")
        # 1. 임베딩 모델 초기화
        logger.info("Start download paraphrase-multilingual-MiniLM-L12-v2")
        self._embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            encode_kwargs={"normalize_embeddings": True},
        )

        # 허깅페이스 모델 사용시 사용될 코드
        #
        # logger.info("Start download Mistral-Small-24B-Instruct-2501")
        # model_id = "timpal0l/mdeberta-v3-base-squad2"  # 사용할 모델의 ID를 지정합니다.
        # # 지정된 모델의 토크나이저를 로드합니다.
        # tokenizer = AutoTokenizer.from_pretrained(model_id)
        # # 지정된 모델을 로드합니다.
        # model = AutoModelForQuestionAnswering.from_pretrained(model_id)
        # # 텍스트 생성 파이프라인을 생성하고, 최대 생성할 새로운 토큰 수를 10으로 설정합니다.
        # pipe = pipeline(
        #     "question-answering", model=model, tokenizer=tokenizer, max_new_tokens=1024
        # )
        # # HuggingFacePipeline 객체를 생성하고, 생성된 파이프라인을 전달합니다.
        # self._llm = HuggingFacePipeline(pipeline=pipe)

    def get_vector_store(self) -> FAISS:
        if self._vector_store is None:
            empty_doc = Document(page_content="")
            self._vector_store = FAISS.from_documents(
                documents=[empty_doc], embedding=self._embeddings
            )
        return self._vector_store

    def add_documents(self, content: str):
        try:
            # 문자열을 Document 객체로 변환
            doc = Document(page_content=content)
            vector_store = self.get_vector_store()
            vector_store.add_documents([doc])
        except Exception as e:
            logger.error(f"Error add_documents: {e}")

    def search_similar_contents(self, query: str) -> str:
        try:
            # 유사한 문서 검색
            retriever = self.get_vector_store().as_retriever(search_kwargs={"k": 3})
            client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
            prompt = client.pull_prompt("rlm/rag-prompt", include_model=True)
            # prompt_template = """당신은 질문 답변 작업을 위한 어시스턴트입니다. 다음의 검색된 컨텍스트 정보를 활용하여 질문에 답변하세요. 답을 모르는 경우, 모른다고 솔직히 말하세요. 최대 3문장으로 답변하고 간결하게 유지하세요.
            #     질문: {question}
            #     컨텍스트: {context}
            #     답변:"""
            # prompt = PromptTemplate.from_template(prompt_template)

            llm = OllamaLLM(
                model="llama3.1",
                base_url="http://host.docker.internal:11434",
            )

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
        except Exception as e:
            logger.error(f"Error search_similar_contents: {e}")

    def clear_store_data(self):
        self._vector_store = None
        self.get_vector_store()
