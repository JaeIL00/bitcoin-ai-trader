from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from vector_store_manager import VectorStoreManager
from pydantic import BaseModel


class ContentInput(BaseModel):
    content: str


app = FastAPI()
vector_store_manager = VectorStoreManager.get_instance()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse(url="/docs", status_code=303)


@app.post("/vector-store/add-content")
async def add_content(body: ContentInput):
    try:
        vector_store_manager.add_documents(body.content)
        return {"status": "success", "message": "Content added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vector-store/get-similar/{query}")
async def get_similar(query: str):
    try:
        response = vector_store_manager.search_similar_contents(query)

        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/vector-store")
async def clear_store():
    try:
        vector_store_manager.clear_store_data()

        return {"status": "success", "message": "Clear successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
