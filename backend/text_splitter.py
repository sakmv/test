
class text_splitter:
    def __init__(self, separator=["\n\n\n", "\n\n", "\n", ".", " ",""]):
        self.separator = separator

#SENTENCE BOUNDARY CHUNKING FROM SCRATCH:
    def sen_bound(self, text, chunk_size, sep):
        chunks = []
        sen = []
        start = 0
        i = 0
        j = 0
        buffer = []

        while i < len(text):
            if [text[i:i+len(sep)]] == [sep]:
                sen.append(text[start:i+len(sep)].strip())
                start = i + len(sep)
                i += len(sep)
            else:
                i += 1

        if start < len(text):
            sen.append(text[start:].strip())

        while j < len(sen):
            if len(" ".join(buffer + [sen[j]])) <= chunk_size:
                buffer.append(sen[j])
            elif buffer:
                chunks.append(" ".join(buffer))
                buffer=[]
                buffer.append(sen[j])
            else:
                chunks.append(sen[j])
            j += 1

        if buffer:
            chunks.append(" ".join(buffer))

        return chunks

#MERGING CHUNKS TO MAXIMIZE CONTEXT IN RAG

    def merge(self, chunks, chunk_size):
        buffer = []
        merged = []
        for chunk in chunks:
            if len(" ".join(buffer + [chunk])) <= chunk_size:
                buffer.append(chunk)
            else:
                if buffer:
                    merged.append(" ".join(buffer))
                    buffer = [chunk]
                else:
                    merged.append(chunk)
        if buffer:
            merged.append(" ".join(buffer))
        return merged
    
#OVERLAPING CHUNKS TO MAINTAIN CONTEXT IN RAG

    def overlap(self,chunks,chunk_size,chunk_overlap):
        if chunk_overlap >= chunk_size:
            print("error overlap too big")
            return chunks
        if chunk_overlap==0:
            return chunks
        chunkf=[]
        chunkf.append(chunks[0])
        for i in range(1,len(chunks)):
            if len(chunks[i])+chunk_overlap<=chunk_size:
                overlap_part=chunks[i-1][-(chunk_overlap):]
            else:
                overlap_part=chunks[i-1][-(chunk_size-len(chunks[i])):]
            fs=overlap_part.find(" ")
            if fs!=-1:
                overlap_part=overlap_part[fs+1:]
            chunkf.append(overlap_part.strip()+" "+chunks[i])
        return chunkf

#ACTUAL RECURSIVE CHUNKING FUNCTION
    def rec_chunk(self, text, chunk_size, chunk_overlap, separator=None,top=True):
        if separator is None:
            separator = self.separator
        final = []
        i = 0
        sep = separator[i]
        chunks = self.sen_bound(text, chunk_size, sep)
        for idx, chunk in enumerate(chunks):
            if len(chunk) > chunk_size:
                if i + 1 < len(separator):
                    final.extend(self.rec_chunk(chunk, chunk_size, chunk_overlap, separator[i+1:], top=False))
                else:
                    print("no")
                    final.append(chunk)
            else:
                final.append(chunk)
        if top:
            return self.overlap(self.merge(final, chunk_size),chunk_size,chunk_overlap)
        return final
