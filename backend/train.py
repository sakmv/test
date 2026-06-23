import pandas as pd
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
df = pd.read_csv("train.csv")
data = list(zip(df["question1"], df["question2"], df["is_duplicate"]))
data = data[:20000]

print(data[0])
class QuoraDataset(Dataset):
    def __init__(self, data, tokenizer, max_len=128):
        self.data = data
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        q1, q2, label = self.data[idx]

        encoding = self.tokenizer(
            q1,
            q2,
            padding="max_length",
            truncation=True,
            max_length=self.max_len,
            return_tensors="pt"
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "label": label
        }
dataset = QuoraDataset(data, tokenizer)

loader = DataLoader(dataset, batch_size=8, shuffle=True)
batch = next(iter(loader))

print(batch["input_ids"].shape)      # should be [8, 128]
print(batch["attention_mask"].shape)
print(batch["label"])