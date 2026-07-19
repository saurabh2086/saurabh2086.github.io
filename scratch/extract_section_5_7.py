import pypdf

pypdf.filters.ZLIB_MAX_OUTPUT_LENGTH = 1000 * 1024 * 1024
pypdf.filters.MAX_DECLARED_STREAM_LENGTH = 1000 * 1024 * 1024

reader = pypdf.PdfReader("bda3/book/BDA3.pdf")

extracted_text = []
for idx in range(137, 142):
    try:
        text = reader.pages[idx].extract_text()
        extracted_text.append(f"=== PDF PAGE INDEX {idx} (BOOK PAGE {idx-9}) ===")
        extracted_text.append(text)
        extracted_text.append("\n" + "="*50 + "\n")
    except Exception as e:
        extracted_text.append(f"Error on PDF page index {idx}: {e}")

with open("scratch/section_5_7.txt", "w") as f:
    f.write("\n".join(extracted_text))

print("Section 5.7 text successfully written to scratch/section_5_7.txt")
