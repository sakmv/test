import torch
from datasets import load_dataset
from torch.utils.data import DataLoader
import torch.nn.functional as F
from encoder import encoder, embed_model, pe, tokenizer

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
encoder.to(device)
embed_model.to(device)
pe.to(device)

def infonce_loss(query_emb, pos_emb, temperature=0.07):
    query_emb = F.normalize(query_emb, dim=-1)
    pos_emb = F.normalize(pos_emb, dim=-1)
    logits = query_emb @ pos_emb.T / temperature
    labels = torch.arange(logits.shape[0]).to(device)
    return F.cross_entropy(logits, labels)

optimizer = torch.optim.AdamW(
    list(encoder.parameters()) + list(embed_model.parameters()),
    lr=2e-4
)

def get_embeddings_batch(texts):
    tokens = tokenizer(texts, return_tensors="pt", truncation=True, max_length=512, padding=True)
    tokens = {k: v.to(device) for k, v in tokens.items()}
    x = embed_model(tokens["input_ids"])
    x = pe(x)
    out = encoder(x)
    return out.mean(dim=1)

def train_step(queries, positives):
    optimizer.zero_grad()
    q_embs = get_embeddings_batch(list(queries))
    p_embs = get_embeddings_batch(list(positives))
    loss = infonce_loss(q_embs, p_embs)
    loss.backward()
    optimizer.step()
    return loss.item()

ds = load_dataset("microsoft/ms_marco", "v1.1", split="train[:5000]")
pairs = []
for row in ds:
    query = row["query"]
    for passage, is_selected in zip(row["passages"]["passage_text"], row["passages"]["is_selected"]):
        if is_selected:
            pairs.append((query, passage))
            break

loader = DataLoader(pairs, batch_size=16, shuffle=True)
encoder.train()
embed_model.train()

for epoch in range(4):
    total_loss = 0
    for queries, positives in loader:
        loss = train_step(list(queries), list(positives))
        total_loss += loss
    print(f"Epoch {epoch+1} loss: {total_loss/len(loader):.4f}")

torch.save({
    'encoder': encoder.state_dict(),
    'embed_model': embed_model.state_dict(),
}, 'encoder_trained.pt')

#WORKED FABULOUSLY YAA WOHHOH