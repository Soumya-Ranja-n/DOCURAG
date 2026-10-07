"""Optional 2-3 query paraphrase generation."""
from app.generation.llm_provider import get_provider
from app.config import get_settings
class QueryRewriter:
    def rewrite(self,q:str)->list[str]:
        if not get_settings().enable_query_rewrite:return [q]
        try:
            text=get_provider().generate("Return only 2-3 concise search paraphrases, one per line.",q)
            vals=[x.strip(" -•\t") for x in text.splitlines() if x.strip()][:3]
            return [q]+[x for x in vals if x.lower()!=q.lower()]
        except Exception:return [q]
