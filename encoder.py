import torch
import torch.nn as nn
import math 
#chunks -->tokenizer---->tokens--->

#-->input embedding layer--->                                           
class InputEmbeddings(nn.Module):
    def __init__(self,d_model: int, vocab: int):
        super().__init__()
        self.d_model=d_model
        self.vocab=vocab #get from tokenizer. no. of unique tokens 
        self.embedding=nn.Embedding(vocab,d_model)

    def forward(self,x):    #input a 2d matrix of batch_size,seq_len (example: sentences rows ,word column matrix)
        return self.embedding(x)*math.sqrt(self.d_model)  #output of 3d matrix with each word hving a vector embedding of size d_model 
    #multiplied by root d to scale it up(originally very small values) so easily measured with positional encodings(-1,1)


#--->positional encoding layer--->
class PositionalEncoding(nn.Module): #add positional encoding to x

    def __init__(self,seq_len,d_model,dropout :float):
        super().__init__()
        self.seq_len=seq_len
        self.d_model=d_model
        self.Dropout=nn.Dropout(dropout)
        pe=torch.zeros(self.seq_len,self.d_model)
        position=torch.arange(0,seq_len,dtype=torch.float()).unsqueeze(1) #arrage is used to make the tensor, then unsqueeze(1) to make it a column seq_len
        #so it corresponds to the seq_len column of pe, which will be added to matrix of seq_len,d_model

        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)) #formula only taking even indices till d_model(2i=even,2i+1=odd)

        pe[:,0::2]=torch.sin(position/div_term)
        pe[:,1::2]=torch.cos(position/div_term)

        pe.unsqueeze(0)
        self.register_buffer('pe',pe)
    def forward(self,x):
        x=x+ self.pe[:,:x.shape[1],:].requires_grad_(False)# so basically we have made pe columns till seq_len(max, token) but x may be till only some less tokens
        return self.Dropout(x)

# ---> Multihead attention-->
class Multihead(nn.Module):
    # ATTENTION(Q,K,V)=SOFTMAX(QK.T/ROOT DK)V
    def __init__(self,d_model:int,h:int,dropout:float):
        super().__init__()
        self.h=h
        assert d_model%h==0,"invalid head value"
        self.dk=d_model//h
        self.wq=nn.Linear(d_model,d_model,bias=False)
        self.wk=nn.Linear(d_model,d_model,bias=False)
        self.wv=nn.Linear(d_model,d_model,bias=False)
        self.wo=nn.Linear(d_model,d_model,bias=False)
        self.dropout=nn.Dropout(dropout)
    @staticmethod
    def attention(query,value,key,dropout:nn.Dropout):
        dk=query.shape[-1]
        at_score=(query@key.transpose(-2,-1))/math.sqrt(dk) #results in matrix of batch,head,sqln,sqln
        at_score=at_score.softmax(dim=-1)
        if dropout is not None:
            at_score=dropout(at_score)
        return(at_score@value),at_score



    def forward(self,q,k,v):
        query=self.wq(q)
        key=self.wk(k)
        value=self.wv(v)
#transpsoe because without it each seqlenn will have head and dk. we want each head to have seq_len and dk. so we swap. also view reshapes and make d_model as dk and h
#essentially we split d_model into dk.
        query=query.view(query.shape[0],query.shape[1],self.h,self.dk).transpose(1,2)
        key=key.view(key.shape[0],key.shape[1],self.h,self.dk).transpose(1,2)
        value=value.view(value.shape[0],value.shape[1],self.h,self.dk).transpose(1,2)

        x,self.attention_scores=Multihead.attention(query,key,value,self.dropout)
        x=x.transpose(1,2) # so seqlen back to its original position.we skipped before
        x=x.contiguous().view(x.shape[0],x.shape[1],self.h*self.dk)
        return self.wo(x)

#--->Normalization-->
class Normalization(nn.Module):
    def __init__(self,d_model: int,e: float=10**(-6)): #formula for norm is x-mean/root of variance+e 
        super().__init__()
        self.e=e
        # now we have two parameters bias(additive) and alpha(multiplicative) which allow model to optimize values accordingly to amplify.otherwise model is restrictive.all mean=0 and var=1.limits learninh
      #ONLY NEED THIS IF WE ARE BUILDING NORM FROM SCRATCH. LAYERNORM ALREADY HAS THESE BUILT IN 
        self.a=nn.Parameter(torch.ones(d_model)) ##originally multiplication should not affect so a*1=a therefore 1
        self.b=nn.Parameter(torch.zeros(d_model)) ##same logic a+0=a these should be changed later by model if needed

    def forward(self,x):
        mean=x.mean(dim=-1,keepdim=True)
        std=x.std(dim=-1,keepdim=True)
        norm=(x-mean)/(self.e+std)
        return ((norm*self.a)+self.b)

##--->Feed Forward---->Normalization
# 2 LINEAR LAYERS WITH A RELU IN E=BETWEEN .RELU IS an activation function that kills negative values

class FeedForward(nn.Module):
    def __init__(self,d_model: int,dff: int,dropout: float):
        super().__init__()
        self.dropout=nn.Dropout(dropout)
        #FINDS PARAMETERS W1 AND B1 CONVERTS MATRICE FROM D_MODEL TO DFF
        self.l1=nn.Linear(d_model,dff,bias=True)
        #FINDS PARAMETERS W2 AND B2 CONVERTS MATRICE FROM DFF TO D_MODEL
        self.l2=nn.Linear(dff,d_model,bias=True)
    
    def forward(self,x):
        x=torch.relu(self.l1(x)) #D_MODEL-->DFF RELU THROWS AWAY NEGATIVES TO 0 --> D_MODEL
        return self.dropout(self.l2(x))

class connector(nn.Module):
    def __init__(self,dropout:float,d_model):
        super().__init__()
        self.drop=nn.Dropout(dropout)
        self.norm=Normalization(d_model)
    def forward(self, x, layer):
        return x + self.drop(self.norm(layer(x)))

class encoderB(nn.Module):
    def __init__(self,multihead:Multihead,ff:FeedForward,drop:float):
        super().__init__()
        self.multihead=multihead
        self.ff=ff
        self.connector1=connector(drop)
        self.connector2=connector(drop)
    
    def forward(self, x, mask):
         x = self.connector1(x, lambda x: self.multihead(x, x, x)) #lamda because we defined connector with sublayer  taking only 1 input. we use 
         #lamda to make it look like we takking 1 but actually using it 3 times 
         x = self.connector2(x, self.ff)
         return x

class Encoder(nn.Module):
    def __init__(self,layers:nn.ModuleList):
        self.layers=layers
        self.norm=Normalization()
    def forward(self,x):
        for layer in self.layers:
            x=layer(x)
        return self.norm(x)

    