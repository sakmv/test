from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import torch
from encoder import encoder, embed_model, pe, tokenizer,get_embedding
import numpy as np
print("before import")

from torch.utils.data import DataLoader
import torch.nn.functional as F
model=SentenceTransformer("all-MiniLM-L6-v2")

# print("before switchig")
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# encoder.to(device)
# embed_model.to(device)
# pe.to(device)
# print(device)
# def infonce_loss(query_emb, pos_emb, temperature=0.07):
#     query_emb = F.normalize(query_emb, dim=-1)
#     pos_emb = F.normalize(pos_emb, dim=-1)
#     logits = query_emb @ pos_emb.T / temperature
#     labels = torch.arange(logits.shape[0]).to(device)
#     return F.cross_entropy(logits, labels)

# optimizer = torch.optim.AdamW(
#     list(encoder.parameters()) + list(embed_model.parameters()),
#     lr=2e-4
# )

# def get_embeddings_batch(texts):
#     tokens = tokenizer(texts, return_tensors="pt", truncation=True, max_length=512, padding=True)
#     tokens = {k: v.to(device) for k, v in tokens.items()}
#     attn_mask = tokens["attention_mask"]                    # (batch, seq_len)

#     x = embed_model(tokens["input_ids"])
#     x = pe(x)

#     encoder_mask = attn_mask[:, None, None, :]               # (batch, 1, 1, seq_len) for broadcasting
#     out = encoder(x, encoder_mask)

#     mask_expanded = attn_mask.unsqueeze(-1).float()           # (batch, seq_len, 1)
#     summed = (out * mask_expanded).sum(dim=1)
#     counts = mask_expanded.sum(dim=1).clamp(min=1e-9)
#     return summed / counts                                    # masked mean, not plain mean

# def train_step(queries, positives):
#     optimizer.zero_grad()
#     q_embs = get_embeddings_batch(list(queries))
#     p_embs = get_embeddings_batch(list(positives))
#     loss = infonce_loss(q_embs, p_embs)
#     loss.backward()
#     optimizer.step()
#     return loss.item()
# print("before loading")
# ds = load_dataset("microsoft/ms_marco", "v2.1", split="train[:500000]")
# print("after loading")
# pairs = []
# for row in ds:
#     query = row["query"]
#     for passage, is_selected in zip(row["passages"]["passage_text"], row["passages"]["is_selected"]):
#         if is_selected:
#             pairs.append((query, passage))
#             break
# print("all fntions")
# loader = DataLoader(pairs, batch_size=16, shuffle=True)
# encoder.train()
# embed_model.train()
# print("training begins")
# for epoch in range(5):
#     total_loss = 0
#     for queries, positives in loader:
#         loss = train_step(list(queries), list(positives))
#         total_loss += loss
#     print(f"Epoch {epoch+1} loss: {total_loss/len(loader):.4f}")

# torch.save({
#     'encoder': encoder.state_dict(),
#     'embed_model': embed_model.state_dict(),
# }, 'encoder_trainedv2.pt')

p1=get_embedding("Large rockets require immense thrust to escape Earth's gravity.")
x1=model.encode("Large rockets require immense thrust to escape Earth's gravity.")
x2=model.encode("Nanorockets are too small to be affected by gravity, and instead face viscous drag.")
p2=get_embedding("Nanorockets are too small to be affected by gravity, and instead face viscous drag.")
r=np.dot(p1,p2)
p=np.dot(x1,x2)
print(f"my model {r}. Sentence transformers : {p}")








#HARD NEGS

# import torch
# import numpy as np
# import bm25s
# print("before import")
# from datasets import load_dataset
# from encoder import encoder, embed_model, pe, tokenizer, get_embedding
# from torch.utils.data import DataLoader
# import torch.nn.functional as F
# print("before switching")
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# encoder.to(device)
# embed_model.to(device)
# pe.to(device)
# print(device)

# def infonce_loss(query_emb, pos_emb, neg_emb, temperature=0.07):
#     query_emb = F.normalize(query_emb, dim=-1)
#     pos_emb = F.normalize(pos_emb, dim=-1)
#     neg_emb = F.normalize(neg_emb, dim=-1)

#     # candidates = [pos_batch ; neg_batch] -> each query's positive is at index i
#     candidates = torch.cat([pos_emb, neg_emb], dim=0)  # (2B, D)
#     logits = query_emb @ candidates.T / temperature    # (B, 2B)
#     labels = torch.arange(query_emb.shape[0]).to(device)  # positive is always index i
#     return F.cross_entropy(logits, labels)

# optimizer = torch.optim.AdamW(
#     list(encoder.parameters()) + list(embed_model.parameters()),
#     lr=2e-4
# )

# def get_embeddings_batch(texts):
#     tokens = tokenizer(list(texts), return_tensors="pt", truncation=True, max_length=512, padding=True)
#     tokens = {k: v.to(device) for k, v in tokens.items()}
#     x = embed_model(tokens["input_ids"])
#     x = pe(x)
#     out = encoder(x)
#     return out.mean(dim=1)

# def train_step(queries, positives, negatives):
#     optimizer.zero_grad()
#     q_embs = get_embeddings_batch(queries)
#     p_embs = get_embeddings_batch(positives)
#     n_embs = get_embeddings_batch(negatives)
#     loss = infonce_loss(q_embs, p_embs, n_embs)
#     loss.backward()
#     optimizer.step()
#     return loss.item()

# print("before loading")
# ds = load_dataset("microsoft/ms_marco", "v2.1", split="train[:500000]")
# print("after loading")

# # Build (query, positive) pairs + a corpus for BM25 mining
# pairs = []
# corpus = []
# for row in ds:
#     query = row["query"]
#     passages = row["passages"]["passage_text"]
#     is_selected = row["passages"]["is_selected"]
#     pos_passage = None
#     for passage, sel in zip(passages, is_selected):
#         if sel:
#             pos_passage = passage
#             break
#     if pos_passage is None:
#         continue
#     pairs.append((query, pos_passage))
#     corpus.extend(passages)  # all passages (pos + distractors) go into the BM25 pool

# print(f"{len(pairs)} pairs, {len(corpus)} corpus passages")
# corpus = list(set(corpus))  # dedupe

# print("building BM25 index")
# corpus_tokens = bm25s.tokenize(corpus, stopwords="en")
# bm25_index = bm25s.BM25()
# bm25_index.index(corpus_tokens)

# # def mine_hard_negative(query, positive_passage, k=10):
# #     q_tokens = bm25s.tokenize(query, stopwords="en")
# #     results, scores = bm25_index.retrieve(query_tokens, k=10, n_threads=12,corpus=corpus)
# #     candidates = [c for c in results[0] if c != positive_passage]
# #     if not candidates:
# #         return positive_passage  # fallback, shouldn't really happen
# #     return candidates[0]  # top BM25 match that isn't the true positive

# print("mining hard negatives")
# queries_list = [q for q, pos in pairs]
# positives_list = [pos for q, pos in pairs]

# query_tokens = bm25s.tokenize(queries_list, stopwords="en")
# results, scores = bm25_index.retrieve(query_tokens, k=10,corpus=corpus,n_threads=14)  # one call for ALL queries

# triplets = []
# for i, (query, pos) in enumerate(pairs):
#     candidates = [c for c in results[i] if c != pos]
#     neg = candidates[0] if candidates else pos
#     triplets.append((query, pos, neg))

# print("all functions ready")
# loader = DataLoader(triplets, batch_size=16, shuffle=True)
# encoder.train()
# embed_model.train()
# print("training begins")
# for epoch in range(5):
#     total_loss = 0
#     for queries, positives, negatives in loader:
#         loss = train_step(list(queries), list(positives), list(negatives))
#         total_loss += loss
#     print(f"Epoch {epoch+1} loss: {total_loss/len(loader):.4f}")

# torch.save({
#     'encoder': encoder.state_dict(),
#     'embed_model': embed_model.state_dict(),
# }, 'encoder_trained_hardneg.pt')
