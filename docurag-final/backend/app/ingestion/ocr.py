"""OCR adapter with PaddleOCR and pytesseract fallback."""
from PIL import Image
from app.config import get_settings
class OCRService:
    def __init__(self): self.engine=get_settings().ocr_engine; self._paddle=None
    import logfire
    @logfire.instrument("OCRService.text")
    def text(self, image: Image.Image) -> str:
        if self.engine == "pytesseract":
            import pytesseract; return pytesseract.image_to_string(image)
        try:
            if self._paddle is None:
                from paddleocr import PaddleOCR
                self._paddle=PaddleOCR(lang="en", use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False)
            import numpy as np
            result=self._paddle.predict(np.asarray(image))
            parts=[]
            for res in result:
                data=getattr(res,"json",lambda: {})()
                rec=data.get("res",data) if isinstance(data,dict) else {}
                texts=rec.get("rec_texts",[]) if isinstance(rec,dict) else []
                parts.extend(texts)
            if parts: return "\n".join(parts)
        except Exception:
            pass
        try:
            import pytesseract; return pytesseract.image_to_string(image)
        except Exception:
            return ""
