"""Stage latency timer."""
from contextlib import contextmanager
from time import perf_counter
class StageTimer:
    def __init__(self): self.timings: dict[str,float] = {}
    @contextmanager
    def stage(self, name: str):
        start=perf_counter()
        try: yield
        finally: self.timings[name]=round((perf_counter()-start)*1000,2)
