import pypdf

pypdf.filters.ZLIB_MAX_OUTPUT_LENGTH = 1000 * 1024 * 1024
pypdf.filters.MAX_DECLARED_STREAM_LENGTH = 1000 * 1024 * 1024

reader = pypdf.PdfReader("bda3/book/BDA3.pdf")
print(f"Total pages: {len(reader.pages)}")

# Search for the term "half-Cauchy" or "Half-Cauchy"
found_pages = []
for idx, page in enumerate(reader.pages):
    try:
        text = page.extract_text().lower()
    except Exception as e:
        continue
    if "half-cauchy" in text or "half-t" in text:
        found_pages.append(idx)
        print(f"Found on page index (0-based): {idx}")

print(f"All matching page indices: {found_pages}")
