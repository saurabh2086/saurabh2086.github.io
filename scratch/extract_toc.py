import pypdf

pypdf.filters.ZLIB_MAX_OUTPUT_LENGTH = 1000 * 1024 * 1024
pypdf.filters.MAX_DECLARED_STREAM_LENGTH = 1000 * 1024 * 1024

reader = pypdf.PdfReader("bda3/book/BDA3.pdf")

# Print TOC pages (index 3 to 10)
for idx in range(3, 10):
    try:
        text = reader.pages[idx].extract_text()
        print(f"=== PAGE INDEX {idx} ===")
        print(text)
        print("\n" + "="*40 + "\n")
    except Exception as e:
        print(f"Error on page {idx}: {e}")
