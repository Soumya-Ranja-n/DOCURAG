"""Route document pages to native text, OCR, or image processing."""
from dataclasses import dataclass
import fitz
@dataclass
class PageRoute:
    page: int; kind: str

def classify_pdf(doc: fitz.Document) -> list[PageRoute]:
    routes=[]
    for i,p in enumerate(doc):
        text=(p.get_text("text") or "").strip()
        images=p.get_images(full=True)
        if text and len(text) >= 80: kind="native"
        elif images and not text: kind="image" if len(images)==1 and p.rect.width*p.rect.height < 1.5e6 else "scanned"
        else: kind="scanned"
        routes.append(PageRoute(i+1,kind))
    return routes
