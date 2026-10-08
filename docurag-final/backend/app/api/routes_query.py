"""Query and SSE streaming endpoints."""
import json, asyncio
from fastapi import APIRouter, Request, Depends
from app.models.schemas import QueryRequest, QueryResponse, Citation
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import rerank
from app.generation.generator import Generator
from app.generation.confidence import confidence,label
from app.utils.timer import StageTimer
from app.deps import verify_api_key, check_rate_limit
router=APIRouter(prefix="/api/query",tags=["query"])
import logfire
@logfire.instrument("run_query")
def run_query(req):
    timer=StageTimer()
    with timer.stage("rewrite"):
        from app.retrieval.query_rewriter import QueryRewriter; queries=QueryRewriter().rewrite(req.question)
    with timer.stage("retrieve"): raw=HybridRetriever().retrieve(req.question,req.top_k,(req.filters or {}).get("doc_ids"))
    with timer.stage("rerank"): ranked=rerank(req.question,raw,req.top_k)
    contexts=[x for x,s in ranked]; scores=[s for x,s in ranked]
    with timer.stage("generate"): answer,self_check=Generator().answer(req.question,contexts) if contexts else ("Not found in the documents.",0.0)
    agreement=len({c.get("doc_id") for c in contexts[:3]})/max(1,min(3,len(contexts))); conf=confidence(scores,agreement,self_check)
    cites=[Citation(doc_name=c["doc_name"],page=c["page"],snippet=c["text"][:400],image_url=(f"/api/documents/{c['doc_id']}/images/{c['image_path'].split('/')[-1]}" if c.get("image_path") else None),score=float(s)) for c,s in ranked]
    timer.timings["total"]=round(sum(timer.timings.values()),2); nf=answer.strip()=="Not found in the documents."
    return QueryResponse(answer=answer,citations=cites,confidence=conf,confidence_label=label(conf),timings_ms=timer.timings,not_found=nf)
@router.post("",response_model=QueryResponse)
@logfire.instrument("API.query")
def query(req:QueryRequest, request: Request, _: bool = Depends(verify_api_key)):
    check_rate_limit(request.client.host if request.client else "unknown"); return run_query(req)
@router.post("/stream")
async def stream(req:QueryRequest, request: Request, _: bool = Depends(verify_api_key)):
    check_rate_limit(request.client.host if request.client else "unknown")
    async def events():
        yield {"event":"status","data":json.dumps({"stage":"retrieving"})}; await asyncio.sleep(0)
        result=run_query(req); yield {"event":"sources","data":json.dumps({"citations":[c.model_dump() for c in result.citations]})}; yield {"event":"confidence","data":json.dumps({"confidence":result.confidence,"label":result.confidence_label})}; yield {"event":"final","data":result.model_dump_json()}
    from sse_starlette.sse import EventSourceResponse
    return EventSourceResponse(events())
