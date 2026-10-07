"""Confidence calculation from reranker, agreement, and LLM self-check."""
def confidence(scores:list[float],agreement:float,self_check:float)->float:
    if not scores:return 0.0
    mn=max(0.0,min(1.0,(scores[0]+1)/2)); mean=max(0.0,min(1.0,(sum(scores[:3])/min(3,len(scores))+1)/2)); return round(.4*mn+.2*mean+.2*agreement+.2*max(0,min(1,self_check)),3)
def label(score:float)->str:return "High" if score>=.75 else "Medium" if score>=.5 else "Low"
