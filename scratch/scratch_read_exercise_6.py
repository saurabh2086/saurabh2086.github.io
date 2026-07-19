import pypdf

reader = pypdf.PdfReader("/Users/turtle/Documents/projects/saurabh2086.github.io/bda3/book/BDA3.pdf")

# Chapter 5 Exercises start on PDF page 143. Let's print out the text of PDF pages 143 and 144.
for page_num in [143, 144]:
    text = reader.pages[page_num].extract_text()
    print(f"--- PDF Page {page_num} ---")
    print(text)
    print("="*60)
