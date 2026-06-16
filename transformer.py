import torch

## CORE CONCEPT:
# ATTENTION(Q,K,V) = softmax(QK^T/ √d_k)*V

# Q --> MATCHES WITH K RETURNS V 
                                                               
#QK^T EVERY TOKEN AGAINST EACH OTHER  

import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class singleHead(nn.Module):
    def __init__(self,d_model,d_k):
        super().__init__()
        self.d_k=d_k
        self.d_model=d_model
        self.W_q=nn.Linear(d_model,d_k,bias=False)
        self.W_k=nn.Linear(d_model,d_k,bias=False)
        self.W_v=nn.Linear(d_model,d_k,bias=False)
        self.F=nn.Linear(d_model,d_k,bias=False)
    def forward(self,X):
        Q=self.W_q(X)
        K=self.W_k(X)
        V=self.W_v(X)
        scores = torch.matmul(Q,K.transpose(-2,-1))
        scores=scores/math.sqrt(self.d_k)
        weight=F.softmax(scores,dim=-1)
        out=torch.matmul(weight,V)
        out=F(out)
        return out,weight

B=2
T=5
d_model=64
d_k=32
x=torch.randn(B,T,d_model)
head = singleHead(64,32)
out,weight=head
print(out.shape)
print(weight.shape)
print(weight[0][0].sum())

















# learning_rate=0.01
# epochs=100

# W=torch.randn(1,1,requires_grad=True)
# b=torch.randn(1,requires_grad=True)
# for epoch in range(epochs):
#     y_hat=X @ W + b
#     loss=torch.mean((y_hat-y_true)**2)
#     loss.backward()
#     with torch.no_grad():
#         W-= learning_rate*W.grad
#         b-=learning_rate*b.grad
#     W.grad.zero_();b.grad.zero_()