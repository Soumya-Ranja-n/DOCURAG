"""Grounded answer generation and self-check."""
import re
from app.generation.llm_provider import get_provider
from app.generation.prompt_builder import build_prompt
class Generator:
    import logfire
    @logfire.instrument("Generator.answer")
    def answer(self,q,contexts):
        system,prompt=build_prompt(q,contexts); images=[c["image_path"] for c in contexts if c.get("image_path")]
        answer=get_provider().generate(system,prompt,images)
        check=get_provider().generate("Return only 1 if the answer is fully supported by context, otherwise 0.",f"Question: {q}\nAnswer: {answer}\nContext: {prompt}")
        return answer,1.0 if re.search(r"\b1\b",check) else 0.0
