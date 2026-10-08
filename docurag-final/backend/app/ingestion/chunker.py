"""Boundary-aware chunking for 300-800 approximate tokens."""
from dataclasses import dataclass
import re
@dataclass
class ChunkData:
    id: str; page: int; type: str; text: str; image_path: str|None=None

import uuid

def _units(text: str) -> list[str]: return re.findall(r"\S+", text)
def chunk_text(text: str, chunk_id_prefix: str, page: int, kind: str="text", image_path: str|None=None, target: int=500, overlap: int=80) -> list[ChunkData]:
    words=_units(text); out=[]; start=0; n=0
    while start<len(words):
        end=min(len(words), start+target); piece=" ".join(words[start:end]).strip()
        if piece:
            chunk_id = str(uuid.uuid5(uuid.NAMESPACE_OID, f"{chunk_id_prefix}-{n}"))
            out.append(ChunkData(chunk_id,page,kind,piece,image_path))
        n+=1
        if end>=len(words): break
        start=max(start+1,end-overlap)
    return out
