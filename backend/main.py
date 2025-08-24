import json
import logging

from cli import (add_user_message, create_body_json, get_knowledge_base_data,
                 make_stream)
from cli import model as ml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FastAPI Backend for Azercelli Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_history = []

class ChatRequest(BaseModel):
    query: str
    system: str | None = None


@app.get("/health")
async def health_check():
    return {"status": "okaydi brat, davam ele"}


@app.post('/chat')
async def chat_endpoint(request: ChatRequest):
    try:
        result = get_knowledge_base_data(user_query=request.query)

        messages = []

        final_prompt = f"""
                        ### Knowledge Base:
                        {result}

                        ### User query:
                        {request.query}
                        """

        add_user_message(messages=messages, prompt=final_prompt)

        body_json = create_body_json(messages=messages, system=request.system)

        stream = make_stream(model=ml, body_json=body_json)

        stream_body = stream.get("body")

        def generate_event():
            try:
                for event in stream_body:
                    stream_chunk = event.get("chunk")
                    decoded = json.loads(stream_chunk.get("bytes").decode("utf-8"))
                    delta = decoded.get("delta", {})
                    text = delta.get("text", "")
                    if text:
                        yield text

            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"[ERROR]: {str(e)}"

        return StreamingResponse(generate_event(), media_type="text/plain")   

    
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        return {"error": f"Error: {str(e)}"}
