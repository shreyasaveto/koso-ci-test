from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.v1.routes import auth_routes, common_routes
from api.v1.routes import ocr_routes, document_routes, customer_routes , project_routes
from api.v1.routes import template_routes
from core.config import settings
from core.logger import setup_logging
from core.logger_config import logger
from db.database import Base, engine

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

Base.metadata.create_all(bind=engine)


@app.get("/", tags=['Welcome'])
def read_root():
    return {"message": "Welcome to the KOSO!"}


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://vakeels.ai",
    "https://de.avetoconsulting.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Logging middleware for  each api request and response

@app.middleware("http")
async def log_request(request: Request, call_next):

    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")

    return response




# app.include_router(routes.router, prefix="/api", tags=["APIs"])
# app.include_router(userSignup_routes.router, tags=["UserSignup"])
app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(customer_routes.router,prefix="/api/v1/customer", tags=["Customer"])
app.include_router(project_routes.router,prefix="/api/v1/project",tags=["Projects"])
app.include_router(document_routes.router, prefix="/api/v1/document" , tags=["Document"])
app.include_router(ocr_routes.router, prefix="/api/v1" ,tags=["OCR"])
app.include_router(template_routes.router, prefix="/api/v1/template" ,tags=["Template"])
app.include_router(common_routes.router, prefix="/api/v1/static",tags=["SeedData"])

setup_logging()

# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import fitz
# import io
# from PIL import Image
# import numpy as np
# import easyocr
# import json
# import base64
#
# backend = FastAPI()
#
# # Allow CORS from React dev server
# backend.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React default port
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# reader = easyocr.Reader(['en'], gpu=False)
#
# def convert_pdf_to_images(pdf_bytes: bytes):
#     doc = fitz.open(stream=pdf_bytes, filetype="pdf")
#     images = []
#     for page in doc:
#         pix = page.get_pixmap(dpi=200)
#         img = Image.open(io.BytesIO(pix.tobytes("png")))
#         images.append(img)
#     return images
#
# def crop_from_bbox(img_np, bbox):
#     x_coords = [point[0] for point in bbox]
#     y_coords = [point[1] for point in bbox]
#     min_x, max_x = int(min(x_coords)), int(max(x_coords))
#     min_y, max_y = int(min(y_coords)), int(max(y_coords))
#     return img_np[min_y:max_y, min_x:max_x]
#
# import logging
#
# @backend.post("/api/ocr-extract/")
# async def ocr_extract(pdf: UploadFile = File(...)):
#     logging.info(f"Received file with content type: {pdf.content_type}")
#     if pdf.content_type != "application/pdf":
#         raise HTTPException(status_code=400, detail="File must be a PDF")
#
#     pdf_bytes = await pdf.read()
#     try:
#         logging.info("Converting PDF to images...")
#         images = convert_pdf_to_images(pdf_bytes)
#         image = images[0]
#         img_np = np.array(image)
#
#         logging.info("Running OCR...")
#         results = reader.readtext(img_np)
#
#         ocr_results = []
#         for bbox, text, conf in results:
#             ocr_results.append({
#                 "bbox": [[int(coord) for coord in point] for point in bbox],  # convert each coordinate to int
#                 "text": text,
#                 "conf": float(conf),
#             })
#
#         buf = io.BytesIO()
#         image.save(buf, format='PNG')
#         base64_img = base64.b64encode(buf.getvalue()).decode()
#
#         logging.info("OCR success, returning results")
#         return {
#             "ocr_results": ocr_results,
#             "image_base64": base64_img,
#         }
#     except Exception as e:
#         logging.error(f"OCR extract error: {e}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))
#
#
#
# @backend.post("/api/apply-kv-on-pdf/")
# async def apply_kv_on_pdf(
#     pdf: UploadFile = File(...),
#     key_value_boxes: str = Form(...)
# ):
#     if pdf.content_type != "application/pdf":
#         raise HTTPException(status_code=400, detail="File must be a PDF")
#
#     try:
#         key_value_boxes_json = json.loads(key_value_boxes)
#     except json.JSONDecodeError:
#         raise HTTPException(status_code=400, detail="Invalid JSON for key_value_boxes")
#
#     pdf_bytes = await pdf.read()
#
#     try:
#         images = convert_pdf_to_images(pdf_bytes)
#         extracted_pairs = []
#
#         for page_num, image in enumerate(images[1:], start=2):  # skip first page
#             img_np = np.array(image)
#
#             for pair in key_value_boxes_json:
#                 key_bbox = pair.get("key_bbox")
#                 value_bbox = pair.get("value_bbox")
#
#                 if not key_bbox or not value_bbox:
#                     continue
#
#                 key_crop = crop_from_bbox(img_np, key_bbox)
#                 value_crop = crop_from_bbox(img_np, value_bbox)
#
#                 key_text = reader.readtext(key_crop, detail=0)
#                 value_text = reader.readtext(value_crop, detail=0)
#
#                 extracted_pairs.append({
#                     "page": page_num,
#                     "key": " ".join(key_text),
#                     "value": " ".join(value_text)
#                 })
#
#         return {"key_value_pairs": extracted_pairs}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
