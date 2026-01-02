from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from pathlib import Path

from app.core.intent import detect_intent
from app.core.retriever import retrieve
from app.core.prompt_builder import build_prompt
from app.vectorstore.index import VectorIndex
from app.llm.gemini_client import ask_gemini

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent.parent

# Load all JSON documents
def load_docs():
    docs = []
    for p in BASE_DIR.rglob("*.json"):
        try:
            with open(p, "r", encoding="utf-8") as f:
                docs.append(json.dumps(json.load(f)))
        except Exception:
            pass
    return docs

ALL_DOCS = load_docs()

# Build vector index ONCE
VECTOR_INDEX = VectorIndex()
VECTOR_INDEX.build(ALL_DOCS)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Empty query"}), 400

    intent = detect_intent(query)

    docs = retrieve(
        query=query,
        intent=intent,
        vector_index=VECTOR_INDEX,
        fallback_docs=ALL_DOCS
    )

    context = "\n\n".join(docs[:3])

    prompt = build_prompt(query, context)

    answer = ask_gemini(prompt)

    return jsonify({
        "intent": intent,
        "response": answer
    })

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Chatbot server is running",
        "message": "Use POST /chat with JSON { query: 'your question' }"
    })


if __name__ == "__main__":
    app.run(debug=True, port=8082)