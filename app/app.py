from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from pathlib import Path

from app.core.intent import detect_intent, find_scholarship, SCHOLARSHIP_ID_TO_SLUG
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

    # Fast path for scholarship queries to return intro + clickable portal link
    if intent == "scholarship":
        scholarship = find_scholarship(query)

        if scholarship:
            scholarship_id = scholarship.get("scholarship_id", "")
            scholarship_name = scholarship.get("scholarship_name", "")
            intro = scholarship.get("intro", "")
            scholarship_slug = SCHOLARSHIP_ID_TO_SLUG.get(scholarship_id, "")
            scholarship_url = f"/scholarship?highlight={scholarship_slug}" if scholarship_slug else ""

            response_text = (
                f"{intro}\n\n"
                "Please go through our scholarship portal for more details.\n"
                f"🔗 View {scholarship_name} Details: {scholarship_url}"
            )

            return jsonify({
                "intent": intent,
                "response": response_text,
                "scholarship_slug": scholarship_slug,
                "scholarship_name": scholarship_name,
                "scholarship_url": scholarship_url,
                "has_scholarship_link": True
            })

    docs = retrieve(
        query=query,
        intent=intent,
        vector_index=VECTOR_INDEX,
        fallback_docs=ALL_DOCS
    )

    # Retriever already returns filtered, parsed context
    context_items = docs if docs is not None else []

    if isinstance(context_items, list):
        context = "\n\n".join(str(item) for item in context_items[:3])
    else:
        context = str(context_items)

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