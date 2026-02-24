# 🔬 SemanticLens — Semantic Search on Research Papers

SemanticLens is a full-stack semantic search tool that lets you search through research papers using natural language queries. It uses a state-of-the-art vector embedding AI model to understand the meaning behind your queries and use vector search (cosine similarity) to find the most relevant papers.

![preview](assets/Screenshot%202026-03-17%20234936.png)

## 📝 Learnings & Challenges

Built this as a coursework experiment to understand how semantic search works under the hood.

- **Embeddings finally clicked** — Implementing L2 normalization and cosine similarity via dot products made the math real in a way lectures didn't. Seeing similar papers cluster in vector space was an "aha" moment.
- **Loading a local model** — Figuring out HuggingFace `transformers`, tokenizer settings, and Qwen3's last-token pooling required a lot of documentation diving. Didn't expect how long the first model download takes.
- **Caching matters** — Recomputing embeddings on every restart was painful. Adding a JSON cache taught me to separate expensive precomputation from the runtime query path.
- **API contract debugging** — Getting the Flask JSON response to match exactly what the JS frontend expected was trickier than anticipated. Small field-name mismatches caused silent failures.
- **Simplicity wins** — Resisting the urge to add a vector DB or React meant I understood every layer end to end. Sometimes the minimal approach teaches you the most.

## 🛠️ Technologies

| Component | Technology |
|-----------|-----------|
| **Backend** | Python Flask |
| **Embedding Model** | [Qwen/Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) (loaded locally via HuggingFace Transformers) |
| **Vector Math** | NumPy (L2 normalization, cosine similarity via dot product) |
| **Frontend** | Vanilla HTML5, CSS3 (Grid/Flexbox), ES6+ JavaScript |
| **API Communication** | Fetch API (JSON over REST) |
| **Data Store** | JSON file (`embedding-vectors.json`) for pre-computed embeddings |

## 🚀 How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

**First run** (computes embeddings — takes a few minutes):
```bash
python app.py
```

![output](assets/Screenshot%202026-03-17%20234956.png)

**Subsequent runs** (loads cached embeddings instantly):
```bash
python app.py
```

**Force recompute embeddings:**
```bash
python app.py --recompute
```

### 3. Open in Browser

Navigate to: [http://localhost:9999](http://localhost:9999)