import pypdf

pypdf.filters.ZLIB_MAX_OUTPUT_LENGTH = 1000 * 1024 * 1024
pypdf.filters.MAX_DECLARED_STREAM_LENGTH = 1000 * 1024 * 1024

reader = pypdf.PdfReader("bda3/book/BDA3.pdf")

# Scan pages 100 to 180 to find where "5.7" is
for idx in range(100, 180):
    try:
        text = reader.pages[idx].extract_text()
    except Exception as e:
        continue
    # Let's print pages containing "5.7" or "Weakly informative"
    if "5.7" in text or "Weakly informative" in text or "half-Cauchy" in text or "half-t" in text:
        print(f"Page index {idx} matches! First 100 chars:")
        print(text[:200].replace('\n', ' '))
        print("-" * 50)
