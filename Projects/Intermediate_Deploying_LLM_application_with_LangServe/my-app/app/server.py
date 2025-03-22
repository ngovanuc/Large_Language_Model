from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI


app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple API server using Langchain's Runnable interfaces",
)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


# Edit this to add the chain you want to add:
# Define a route for the OpenAI chat model
add_routes(
    app, 
    ChatOpenAI(),
    path="./openai"
    # NotImplemented
)

# Define a route with a custom prompt
summarize_prompt = ChatPromptTemplate.from_template("Summarize the following text: {text}")
add_routes(
    app,
    summarize_prompt | ChatOpenAI(),
    path="./summarize"
)

# Chúng ta cũng có thể thêm một route và prompt tùy ý
joke = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
add_routes(
    app,
    joke | ChatOpenAI(),
    path="./joke",
)

# Start Prometheus server
start_http_server(8001)

# Define a Prometheus metric
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

app = FastAPI()

# Middleware for tracking request processing time
@app.middleware("http")
async def add_prometheus_middleware(request: Request, call_next):
	start_time = time.time()
	response = await call_next(request)
	duration = time.time() - start_time
	REQUEST_TIME.observe(duration)
	return response


@app.get("/health")
async def health():
    return {"status": "Healthy"}


@app.exception_handler(HTTPException)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"An error occurredL {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error occurred: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
