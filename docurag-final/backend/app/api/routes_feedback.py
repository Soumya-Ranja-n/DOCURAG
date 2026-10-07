from fastapi import APIRouter
from app.models.db import Feedback,SessionLocal
from app.models.schemas import FeedbackRequest
router=APIRouter(prefix="/api/feedback",tags=["feedback"])
@router.post("")
def feedback(req:FeedbackRequest):
    db=SessionLocal(); db.add(Feedback(query=req.query,rating=req.rating,comment=req.comment)); db.commit(); db.close(); return {"ok":True}
