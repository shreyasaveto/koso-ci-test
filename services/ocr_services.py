import fitz
import io
import numpy as np
from PIL import Image
import easyocr
import base64
import json
import logging
from fastapi import UploadFile, HTTPException

reader = easyocr.Reader(['en'], gpu=False)

def convert_pdf_to_images(pdf_bytes: bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return [Image.open(io.BytesIO(page.get_pixmap(dpi=200).tobytes("png"))) for page in doc]

def crop_from_bbox(img_np, bbox):
    x_coords = [pt[0] for pt in bbox]
    y_coords = [pt[1] for pt in bbox]
    return img_np[int(min(y_coords)):int(max(y_coords)), int(min(x_coords)):int(max(x_coords))]

def extract_text_from_image(image: Image.Image):
    img_np = np.array(image)
    results = reader.readtext(img_np)
    return [
        {
            "bbox": [[int(coord) for coord in pt] for pt in bbox],
            "text": text,
            "conf": float(conf),
        }
        for bbox, text, conf in results
    ]


# async def process_ocr(pdf: UploadFile):
#     if pdf.content_type != "application/pdf":
#         raise HTTPException(status_code=400, detail="File must be a PDF")

#     try:
#         pdf_bytes = await pdf.read()
#         images = convert_pdf_to_images(pdf_bytes)
#         image = images[0]
#         img_np = np.array(image)

#         results = reader.readtext(img_np)
#         ocr_results = []

#         for idx, (bbox, text, conf) in enumerate(results):
#             ocr_results.append({
#                 "id": f"b{idx}",
#                 "bbox": [[int(coord) for coord in pt] for pt in bbox],
#                 "text": text,
#                 "conf": float(conf),
#             })

#         # Convert image to base64 for preview
#         buf = io.BytesIO()
#         image.save(buf, format="PNG")
#         base64_img = base64.b64encode(buf.getvalue()).decode()

#         return {
#             "ocr_results": ocr_results,
#             "image_base64": base64_img,
#         }

#     except Exception as e:
#         logging.exception("OCR extraction failed")
#         raise HTTPException(status_code=500, detail="OCR extraction error")



async def process_kv_extraction(pdf: UploadFile, key_value_boxes: str):
    if pdf.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        kv_boxes = json.loads(key_value_boxes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid key_value_boxes JSON")

    try:
        pdf_bytes = await pdf.read()
        images = convert_pdf_to_images(pdf_bytes)
        extracted_pairs = []

        for page_num, image in enumerate(images[1:], start=2):  # skip first page
            img_np = np.array(image)
            for pair in kv_boxes:
                key_bbox = pair.get("key_bbox")
                value_bbox = pair.get("value_bbox")
                if not key_bbox or not value_bbox:
                    continue

                key_crop = crop_from_bbox(img_np, key_bbox)
                value_crop = crop_from_bbox(img_np, value_bbox)

                key_text = " ".join(reader.readtext(key_crop, detail=0))
                value_text = " ".join(reader.readtext(value_crop, detail=0))

                extracted_pairs.append({
                    "page": page_num,
                    "key": key_text,
                    "value": value_text
                })

        return {"key_value_pairs": extracted_pairs}

    except Exception as e:
        logging.exception("Key-value extraction failed")
        raise HTTPException(status_code=500, detail="Key-value extraction error")


async def process_ocr(pdf_bytes: bytes, pages: int):
    # if pdf_bytes.content_type != "application/pdf":
    #     raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        images = convert_pdf_to_images(pdf_bytes)
        ocr_results = []
        image_list = []
        for i in range(pages):
            image = images[i]
            img_np = np.array(image)
            results = reader.readtext(img_np)
            page_ocr = []
            for idx, (bbox, text, conf) in enumerate(results):
                page_ocr.append({
                    "id": f"b{idx}",
                    "bbox": [[int(coord) for coord in pt] for pt in bbox],
                    "text": text,
                    "conf": float(conf),
                })
            ocr_results.append({
                "page" : i+1,
                "ocr" : page_ocr 
            })

            #get list of images
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            base64_img = base64.b64encode(buf.getvalue()).decode()
            image_list.append(base64_img)
        return {
            "ocr_results": ocr_results,
            "image_base64": image_list,
        }

    except Exception as e:
        logging.exception("OCR extraction failed")
        raise HTTPException(status_code=500, detail="OCR extraction error")