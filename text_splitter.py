text = open("input.txt", "r").read()
def fixed_size(text,chunk_size,chunk_overlap):
    chunks = []
    i=0
    while i < len(text):
        end=i+chunk_size
        chunks.append(text[i:end])
        i=end-chunk_overlap
    return chunks

    
def sen_bound(text,chunk_size,overlap=1):
    chunks=[]
    sen=[]
    start=0
    i=0
    j=0
    buffer=[]
    while i<len(text):
        if text[i] in '.!?':
            sen.append(text[start:i+1].strip())
            start=i+1
        i=i+1
    while j < len(sen):
        print(len(sen))
        if sum(len(s) for s in buffer)+len(sen[j])<=chunk_size:
            buffer.append(sen[j])
        elif buffer:
            chunks.append(" ".join(buffer))
            buffer=buffer[-overlap:]
            buffer.append(sen[j])
           
        j=j+1
    if buffer:
         chunks.append(" ".join(buffer))
    return chunks




while 1:
     print("Choose strategy: 1.fixed size 2.sentence boundary")
     ch = int(input("enter: "))
     if ch==1:
        chunk=fixed_size(text,50,20)
     elif ch==2:
        chunk=sen_bound(text,500)
     elif ch==-1:
         break

     for i in range(0,len(chunk)):
        print("chunk ",i,":",chunk[i])
     print("total chunks are",len(chunk))
