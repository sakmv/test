# import torch
# import torch.nn as nn
# import json
# import random
# import os
# from datasets import load_dataset

# # generate training data if not exists
# if not os.path.exists("training_pairs.json"):
#     ds = load_dataset("ms_marco", "v2.1", split="train")
#     pairs = []
#     for item in ds:
#         query = item["query"]
#         for passage in item["passages"]["passage_text"]:
#             pairs.append({"question": query, "chunk": passage})
#         if len(pairs) >= 2000:
#             break
#     with open("training_pairs.json", "w") as f:
#         json.dump(pairs, f)
#     print("saved training_pairs.json")
# else:
#     with open("training_pairs.json", "r") as f:
#         pairs = json.load(f)
#     print(f"loaded {len(pairs)} pairs")

# from encoder import embed_model, pe_model, encoder_model, tokenizer

# all_chunks = list(set(p["chunk"] for p in pairs))

# def get_embedding_train(text):
#     tokens = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
#     x = embed_model(tokens["input_ids"])
#     x = pe_model(x)
#     out = encoder_model(x)
#     return out.mean(dim=1).squeeze(0)

# loss_fn = nn.TripletMarginLoss(margin=1.0)
# params = list(embed_model.parameters()) + list(pe_model.parameters()) + list(encoder_model.parameters())
# optimizer = torch.optim.Adam(params, lr=1e-4)

# embed_model.train()
# pe_model.train()
# encoder_model.train()

# EPOCHS = 5

# for epoch in range(EPOCHS):
#     random.shuffle(pairs)
#     total_loss = 0

#     for pair in pairs:
#         anchor = get_embedding_train(pair["question"])
#         positive = get_embedding_train(pair["chunk"])

#         neg_chunk = pair["chunk"]
#         while neg_chunk == pair["chunk"]:
#             neg_chunk = random.choice(all_chunks)
#         negative = get_embedding_train(neg_chunk)

#         loss = loss_fn(anchor.unsqueeze(0), positive.unsqueeze(0), negative.unsqueeze(0))
#         optimizer.zero_grad()
#         loss.backward()
#         optimizer.step()
#         total_loss += loss.item()

#     print(f"epoch {epoch+1}/{EPOCHS} loss: {total_loss/len(pairs):.4f}")

# torch.save({
#     "embed": embed_model.state_dict(),
#     "pe": pe_model.state_dict(),
#     "encoder": encoder_model.state_dict()
# }, "finetuned.pt")

# print("saved to finetuned.pt")