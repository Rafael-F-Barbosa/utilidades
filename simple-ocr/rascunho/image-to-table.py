from img2table.ocr import TesseractOCR
from img2table.document import Image


src = "output_images/page_2.jpg"

# Instantiation of OCR
ocr = TesseractOCR(n_threads=1, lang="eng")

# Instantiation of document, either an image or a PDF
doc = Image(src)

# Table extraction
extracted_tables = doc.extract_tables(ocr=ocr,
                                      implicit_rows=False,
                                      implicit_columns=False,
                                      borderless_tables=False,
                                      min_confidence=50)


table = extracted_tables[0]
print(table)

for id_row, row in enumerate(table.content.values()):
    print()
    print()
    print()

    for cell in row:
        # x1 = cell.bbox.x1
        # y1 = cell.bbox.y1
        # x2 = cell.bbox.x2
        # y2 = cell.bbox.y2
        value = cell.value
        print(value)