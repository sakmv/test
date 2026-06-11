text = open("input.txt", "r").read()
## RECCURSIVE CHUNKING TEXT-SPLITTER FROM SCRATCH
separator=["\n\n\n","\n\n","\n","."," ",""]
def rec_chunk(text,chunk_size,chunk_overlap,separator):
    final=[]
    i=0
    sep=separator[i]
    chunks=sen_bound(text,chunk_size,sep,chunk_overlap)
    for chunk in chunks:
       if(len(chunk)>chunk_size):
          if(i+1<len(separator)):
             chunks.replace(chunk,rec_chunk(chunk,chunk_size,chunk_overlap,separator[i+1:]))
          else:
             print("no fallback separator reamining")
    


## SUDO CODE FOR OTHER TEXT SPLITTING STRATEGIES FROM SCRATCH:

#STRATEGRY 1. FIXED SIZE CHUNKING:


# def fixed_size(text,chunk_size,chunk_overlap):
#     if(chunk_overlap>=chunk_size):
#         print("Overlap cannot be greater than or equal to chunk size")
#         return []
#     chunks = []
#     i=0
#     while i < len(text):
#         end=i+chunk_size
#         chunks.append(text[i:end])
#         i=end-chunk_overlap
#     print(chunks)
#     return chunks

#STRATEGY 2. SENTENCE BOUNDARY CHUNKING:
def sen_bound(text, chunk_size, sep, overlap=1):
     chunks = []
     sen = []
     start = 0
     i = 0
     j = 0
     buffer = []

     while i < len(text):
         if text[i] in sep:
            sen.append(text[start:i+1].strip())
            start = i + 1
         i += 1

     if start < len(text):
         sen.append(text[start:].strip())

     while j < len(sen):
         if len(" ".join(buffer + [sen[j]])) <= chunk_size:
            buffer.append(sen[j])
         elif buffer:
            chunks.append(" ".join(buffer))
            buffer = buffer[-overlap:]
            buffer.append(sen[j])
         else:
            chunks.append(sen[j])
         j += 1

     if buffer:
        chunks.append(" ".join(buffer))

     return chunks
    
result=sen_bound(text, 500, separator[3], 1)
print(result[0])