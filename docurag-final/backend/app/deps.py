"""Request security dependencies."""
from collections import defaultdict,deque
from time import monotonic
from fastapi import Header,HTTPException
from app.config import get_settings
_buckets=defaultdict(deque)
def verify_api_key(x_api_key:str|None=Header(default=None)):
 s=get_settings()
 if s.api_key and x_api_key!=s.api_key: raise HTTPException(401,"Invalid API key")
 return True
def check_rate_limit(client_key:str):
 s=get_settings(); now=monotonic(); q=_buckets[client_key]
 while q and now-q[0]>60:q.popleft()
 if len(q)>=s.query_rate_limit_per_minute: raise HTTPException(429,"Query rate limit exceeded")
 q.append(now)
