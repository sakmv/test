from text_splitter import text_splitter

text = open("input.txt", "r").read()

splitter=text_splitter()
chunks=splitter.rec_chunk(text,500,50)
print(chunks[0])