import torch
learning_rate=0.01
epochs=100

W=torch.randn(1,1,requires_grad=True)
b=torch.randn(1,requires_grad=True)
for epoch in range(epochs):
    y_hat=X @ W + b
    loss=torch.mean((y_hat-y_true)**2)
    loss.backward()
    with torch.no_grad():
        W-= learning_rate*W.grad
        b-=learning_rate*b.grad
    W.grad.zero_();b.grad.zero_()