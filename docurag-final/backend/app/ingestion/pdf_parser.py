"""PDF parsing, page rendering, and figure extraction."""
from pathlib import Path
import hashlib, fitz
from PIL import Image
from app.ingestion.router import classify_pdf
from app.ingestion.ocr import OCRService
from app.ingestion.table_extractor import tables_for_page

import logfire
@logfire.instrument("parse_pdf")
def parse_pdf(path: str, image_dir: str) -> tuple[list[dict],int]:
    doc=fitz.open(path); routes=classify_pdf(doc); ocr=OCRService(); records=[]
    Path(image_dir).mkdir(parents=True,exist_ok=True)
    for route in routes:
        p=doc[route.page-1]; text=""
        if route.kind=="native": text=p.get_text("text")
        else:
            pix=p.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False); data=pix.tobytes("png"); img_path=Path(image_dir)/f"page-{route.page}.png"; img_path.write_bytes(data)
            text=ocr.text(Image.open(img_path))
        records.append({"page":route.page,"type": "ocr" if route.kind!="native" else "text","text":text,"image_path":None})
        for t in tables_for_page(path,route.page): records.append({"page":route.page,"type":"table","text":t,"image_path":None})
        for idx,img in enumerate(p.get_images(full=True)):
            try:
                xref=img[0]; raw=doc.extract_image(xref); ext=raw["ext"]; payload=raw["image"]; digest=hashlib.sha256(payload).hexdigest()[:16]
                if len(payload)<15000: continue
                fp=Path(image_dir)/f"p{route.page}-{digest}.{ext}"; fp.write_bytes(payload)
                records.append({"page":route.page,"type":"figure","text":"","image_path":str(fp)})
            except Exception: continue
    doc.close(); return records,len(routes)

@logfire.instrument("parse_image")
def parse_image(path: str, image_dir: str)->tuple[list[dict],int]:
    p=Path(path); target=Path(image_dir)/p.name; target.write_bytes(p.read_bytes()); text=OCRService().text(Image.open(target)); return [{"page":1,"type":"ocr","text":text,"image_path":str(target)}],1
