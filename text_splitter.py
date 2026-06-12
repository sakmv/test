text = open("input.txt", "r").read()

#SENTENCE BOUNDARY CHUNKING FROM SCRATCH:

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
    
## RECCURSIVE CHUNKING TEXT-SPLITTER FROM SCRATCH

separator=["\n\n\n","\n\n","\n","."," "]

#MERGE FUNCTION FOR FINAL MERGING 

def merge(chunks,chunk_size,chunk_overlap):
    buffer=[]
    merged=[]
    for chunk in chunks:
      if(len(" ".join(buffer+[chunk]))<=chunk_size):
         buffer.append(chunk)
      else:
         if buffer:
            merged.append(" ".join(buffer))
         overlap = buffer[-chunk_overlap:] if chunk_overlap else []
         if len(" ".join(overlap + [chunk])) <= chunk_size:
            buffer = overlap  
         else:
                buffer = []
         buffer.append(chunk)
    if buffer:
       merged.append(" ".join(buffer))
    return merged

def rec_chunk(text,chunk_size,chunk_overlap,separator):
    final=[]
    i=0
    sep=separator[i]
    chunks=sen_bound(text,chunk_size,sep,chunk_overlap)
    for idx,chunk in enumerate(chunks):
       if(len(chunk)>chunk_size):
          if(i+1<len(separator)):
             final.extend(rec_chunk(chunk,chunk_size,chunk_overlap,separator[i+1:]))
             
          else:
             print("no")
             final.append(chunk)
       else:
          final.append(chunk)
          
    return merge(final,chunk_size,chunk_overlap)

chunk=rec_chunk(text,500,1,separator)
for idx,c in enumerate(chunk):
   print("chunk ",idx," value: ",c)

# STRATEGRY : FIXED SIZE CHUNKING (NOT GOOD FOR RAG AS IT DOESNT RESPECT CONTEXT)

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
