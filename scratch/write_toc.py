import pypdf

pypdf.filters.ZLIB_MAX_OUTPUT_LENGTH = 1000 * 1024 * 1024
pypdf.filters.MAX_DECLARED_STREAM_LENGTH = 1000 * 1024 * 1024

reader = pypdf.PdfReader("bda3/book/BDA3.pdf")

# Extract and write TOC pages 3 to 7
with open("scratch/toc_text.txt", "w") as f:
    for idx in range(3, 8):
        try:
            text = reader.pages[idx].extract_text()
            f.write(f"=== PAGE INDEX {idx} ===\n")
            f.write(text)
            f.write("\n\n" + "="*40 + "\n\n")
        except Exception as e:
            f.write(f"Error on page {idx}: {e}\n")
print("TOC pages written to scratch/toc_text.txt")
