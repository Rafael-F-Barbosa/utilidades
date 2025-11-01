import argparse
from pdf2image import convert_from_path
import os
from img2table.ocr import TesseractOCR
from img2table.document import Image
import sys
from manipulacao_textos import *
import json

impressao_ativa = False

def impressao(valor = ''):
    if impressao_ativa:
        print(valor)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,
    help="path to input PDF or image file to be OCR'd")
ap.add_argument("-o", "--output", default="output_images",
    help="directory to save intermediate JPEG images")

args = vars(ap.parse_args())

input_path = args["input"]
output_dir = args["output"]

os.makedirs(output_dir, exist_ok=True)
text = ""

# Silencia temporariamente mensagens do Tesseract
sys.stderr = open(os.devnull, 'w')

ocr = TesseractOCR(n_threads=1, lang="eng")

# Restaura stderr após inicialização
sys.stderr = sys.__stderr__


lista_gastos = []

if input_path.lower().endswith(".pdf"):
    images = convert_from_path(input_path)

    for i, page in enumerate(images):
        # Define JPEG output path
        image_path = os.path.join(output_dir, f"page_{i+1}.jpg")

        # Save as JPEG
        page.save(image_path, "JPEG")
        impressao(f"[INFO] Saved: {image_path}")

        # Instantiation of document, either an image or a PDF
        doc = Image(image_path)

        # Extrai tabelas
        extracted_tables = doc.extract_tables(ocr=ocr,
                                      implicit_rows=False,
                                      implicit_columns=False,
                                      borderless_tables=False,
                                      min_confidence=50)
        
        if (len(extracted_tables) >= 1):
            table = extracted_tables[0]

            anteriorEhData = False

            for id_row, row in enumerate(table.content.values()):
                impressao()
                impressao("Linha: ")

                ehData, ehBR, ehDinheiro = False, False, False

                gasto = {}

                for cell in row:
                    value = cell.value

                    ehData = verifica_data_dia_mes(value)
                    ehBR = (value == 'BR')
                    ehDinheiro = verifica_valor_monetario(value)

                    if anteriorEhData and not (ehBR or ehData or ehDinheiro):
                        gasto['nome'] = value
                        anteriorEhData = False

                    elif ehData:
                        gasto["data"] = value
                        impressao("É data: " + value)
                        anteriorEhData = True
                    elif ehBR:
                        continue
                    elif ehDinheiro:
                        gasto["valor"] = converte_valor_monetario(value)
                        impressao("É dinheiro: " + value)
                    else:
                        impressao(value)

                if "data" in gasto and "valor" in gasto:
                    lista_gastos.append(gasto)
                impressao()
else:
    print("A fatura deve estar no formato .pdf")


lista_gastos_formatada = []
soma = 0
for g in lista_gastos:
    print(f'Data {g["data"]} Nome {g["nome"]} Valor {g["valor"]}')
    print()
    if g['valor'] > 0:
        soma += g['valor']
        lista_gastos_formatada.append({
                "nome": g["nome"],
                "valor": g['valor'],
                "data": g['data'] + "/2025"
            }
        )

with open("dados-fatura.json", "w", encoding="utf-8") as f:
    json.dump(lista_gastos_formatada, f, indent=4, ensure_ascii=False)

print("Soma total dos gastos: ", soma)