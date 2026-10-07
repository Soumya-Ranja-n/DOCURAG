"""Offline evaluation harness for Recall@5, MRR, and latency."""
import json,time,sys
from pathlib import Path
from app.retrieval.hybrid_retriever import HybridRetriever

def main():
 qs=json.loads(Path(__file__).with_name('test_questions.json').read_text()); hit=0;rr=0;lat=[]
 for q in qs:
  t=time.perf_counter(); rows=HybridRetriever().retrieve(q['question'],5); lat.append((time.perf_counter()-t)*1000); ids={x.get('doc_name') for x in rows}; expected=set(q.get('expected_docs',[])); ranks=[i+1 for i,x in enumerate(rows) if x.get('doc_name') in expected]
  if ranks: hit+=1;rr+=1/ranks[0]
 n=len(qs) or 1; print(json.dumps({'Recall@5':hit/n,'MRR':rr/n,'avg_latency_ms':sum(lat)/max(1,len(lat))},indent=2))
if __name__=='__main__':main()
