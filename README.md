
---

## 1. Hybrid Retrieval System
- Combines **Dense Retrieval (Embeddings)** + **BM25 keyword search**
- Merges results to improve recall for both semantic + exact-match queries
- Significantly improves retrieval robustness across document types

---

## 2. Cross-Encoder Re-ranking  done
- Uses a **cross-encoder model to re-score retrieved chunks**
- Improves ranking quality by evaluating query–chunk pairs jointly
- Enhances final context relevance before LLM generation

---

## 3. Evaluation Framework (ML Benchmarking)
- Built a labeled dataset of **question → expected chunk mappings**
- Computes:
  - Hit@K
  - Mean Reciprocal Rank (MRR)
  - Precision@K
- Enables systematic comparison of retrieval strategies

---

## 4. Confidence Scoring & Answer Reliability
- Generates confidence scores using retrieval + reranker signals
- Flags low-confidence responses when evidence is weak
- Reduces hallucinations by enforcing evidence-based answering

---

## 5. Document Intelligence Features
- Supports PDF ingestion with chunking + metadata tracking
- Returns **source citations with answers**
- Enables downloadable Q&A reports (question, answer, sources, confidence)

train encoder