from app.ingestion.chunker import chunk_text
from app.generation.confidence import confidence,label

def test_chunk_bounds():
 c=chunk_text(' '.join(['word']*1200),'x',1); assert len(c)>=2; assert all(1<=len(x.text.split())<=500 for x in c)
def test_confidence():
 x=confidence([0.8,0.6,0.4],1,1); assert .5<x<=1; assert label(x) in {'Medium','High'}
