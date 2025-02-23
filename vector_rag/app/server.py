from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaEmbeddings  # 변경
from langchain_community.vectorstores import FAISS
from langserve import add_routes
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM  # 변경

app = FastAPI()

# Ollama 설정
embeddings = OllamaEmbeddings(model="llama3.2:1b", base_url="http://ollama:11434")
llm = OllamaLLM(model="llama3.2:1b", base_url="http://ollama:11434")

vectorstore = FAISS.from_texts(["뉴스 분석용 초기 데이터"], embeddings)
retriever = vectorstore.as_retriever()

chain = (
    {"context": retriever, "question": RunnablePassthrough()} | llm | StrOutputParser()
)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse(url="/docs", status_code=303)


@app.post("/add_content")
async def add_content(content_input: str):
    try:
        # 새로운 컨텐츠를 벡터 저장소에 추가
        vectorstore.add_texts([content_input])

        # 검색기 업데이트
        global retriever
        retriever = vectorstore.as_retriever()

        return {"status": "success", "message": "Content added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_similar/{query}")
async def get_similar(query: str):
    try:
        # 유사한 문서 검색
        docs = retriever.get_relevant_documents(query)
        return {"similar_documents": [doc.page_content for doc in docs]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 라우트 추가
add_routes(app, chain)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
