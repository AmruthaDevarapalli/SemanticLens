import os
import json
import glob
import argparse
import numpy as np
from flask import Flask, request, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

RESEARCH_PAPERS_DIR = os.path.join(BASE_DIR, 'research-papers')
EMBEDDINGS_FILE = os.path.join(BASE_DIR, 'embedding-vectors.json')
MAX_PAPERS = 100

model = None
tokenizer = None


def load_model():
    """Load Qwen3-Embedding-0.6B model and tokenizer."""
    global model, tokenizer
    if model is not None:
        return
    from transformers import AutoModel, AutoTokenizer
    print("🔄 Loading Qwen/Qwen3-Embedding-0.6B model...")
    model_name = "Qwen/Qwen3-Embedding-0.6B"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    print("✅ Model loaded successfully!")


def compute_embedding(text):
    """Compute L2-normalized embedding for a given text."""
    import torch
    load_model()
    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    # Qwen3-Embedding uses last-token pooling (decoder-only model)
    last_token_idx = inputs['attention_mask'].sum(dim=1) - 1
    embedding = outputs.last_hidden_state[0, last_token_idx[0], :].float().numpy()
    # L2 normalization
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    return embedding.tolist()


def read_paper(filepath):
    """Read a research paper file and return its content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def parse_paper(content):
    """Parse paper content into structured fields."""
    fields = {}
    for line in content.strip().split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            fields[key.strip()] = value.strip()
    return fields


def generate_embeddings(recompute=False):
    """Generate embeddings for research papers and save to JSON."""
    if os.path.exists(EMBEDDINGS_FILE) and not recompute:
        print(f"📂 Loading existing embeddings from {EMBEDDINGS_FILE}")
        return

    print("📊 Computing embeddings for research papers...")
    paper_files = sorted(glob.glob(os.path.join(RESEARCH_PAPERS_DIR, '*.txt')))[:MAX_PAPERS]
    print(f"📄 Found {len(paper_files)} papers to process")

    embeddings = []
    for i, filepath in enumerate(paper_files):
        content = read_paper(filepath)
        paper = parse_paper(content)
        paper_id = paper.get('id', os.path.basename(filepath).replace('.txt', ''))

        # Use title + abstract for embedding
        text_for_embedding = f"{paper.get('title', '')} {paper.get('abstract', '')}"
        vector = compute_embedding(text_for_embedding)

        embeddings.append({
            "vector": vector,
            "id": paper_id
        })

        if (i + 1) % 10 == 0:
            print(f"  ✅ Processed {i + 1}/{len(paper_files)} papers")

    with open(EMBEDDINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(embeddings, f)
    print(f"💾 Saved {len(embeddings)} embeddings to {EMBEDDINGS_FILE}")


def load_embeddings():
    """Load embeddings from JSON file."""
    with open(EMBEDDINGS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def cosine_similarity_search(query_vector, embeddings, top_k=3):
    """Perform cosine similarity search (dot product since vectors are L2-normalized)."""
    query = np.array(query_vector)
    results = []
    for entry in embeddings:
        doc_vector = np.array(entry['vector'])
        score = float(np.dot(query, doc_vector))
        results.append({
            'id': entry['id'],
            'score': score
        })
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_k]


@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/styles.css')
def styles():
    """Serve CSS file."""
    return send_from_directory(BASE_DIR, 'styles.css')


@app.route('/script.js')
def scripts():
    """Serve JavaScript file."""
    return send_from_directory(BASE_DIR, 'script.js')


@app.route('/api/search', methods=['POST'])
def search():
    """Handle semantic search requests."""
    data = request.get_json()
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'error': 'Query cannot be empty'}), 400

    # Compute embedding for the query
    query_vector = compute_embedding(query)

    # Load stored embeddings
    embeddings = load_embeddings()

    # Perform similarity search
    top_results = cosine_similarity_search(query_vector, embeddings)

    # Enrich results with paper content
    results = []
    for r in top_results:
        paper_path = os.path.join(RESEARCH_PAPERS_DIR, f"{r['id']}.txt")
        if os.path.exists(paper_path):
            content = read_paper(paper_path)
            paper = parse_paper(content)
            results.append({
                'id': r['id'],
                'score': round(r['score'], 4),
                'title': paper.get('title', 'Unknown'),
                'year': paper.get('year', 'N/A'),
                'authors': paper.get('authors', '[]'),
                'venue': paper.get('venue', 'N/A'),
                'abstract': paper.get('abstract', 'No abstract available'),
                'content': content
            })

    return jsonify({'results': results})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SemanticLens - Semantic Search on Research Papers')
    parser.add_argument('--recompute', action='store_true', help='Recompute embeddings even if they exist')
    args = parser.parse_args()

    generate_embeddings(recompute=args.recompute)
    print("🚀 Starting SemanticLens on http://localhost:9999")
    app.run(host='0.0.0.0', port=9999, debug=False)
