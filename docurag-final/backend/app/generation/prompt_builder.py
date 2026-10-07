"""Grounded generation prompt construction."""
SYSTEM="""You are DocuRAG, a document-grounded assistant. Answer ONLY from the supplied context. Cite claims using [document name, p.X]. If the context does not support the answer, respond exactly: Not found in the documents. Never invent facts, numbers, pages, or citations."""
def build_prompt(question,contexts):
    blocks=[]
    for i,c in enumerate(contexts,1): blocks.append(f"[{i}] {c['doc_name']} p.{c['page']} ({c['type']})\n{c['text']}")
    return SYSTEM,"Question: "+question+"\n\nContext:\n"+"\n\n".join(blocks)
