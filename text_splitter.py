text = open("input.txt", "r").read()

def fixed_size(text,chunk_size,chunk_overlap):
    chunks = []
    i=0
    while i < len(text):
        end=i+chunk_size
        chunks.append(text[i:end])
        i=end-chunk_overlap
    return chunks

chunk=fixed_size(text,50,20);
for i in range(0,len(chunk)):
    print("chunk ",i,":",chunk[i])
print("total chunks are",len(chunk))
    
