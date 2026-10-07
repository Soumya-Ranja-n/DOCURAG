"""Extract PDF tables as compact markdown."""
import pdfplumber

def tables_for_page(pdf_path: str, page_number: int) -> list[str]:
    output=[]
    with pdfplumber.open(pdf_path) as pdf:
        page=pdf.pages[page_number-1]
        for table in page.extract_tables() or []:
            rows=[[str(c or "").replace("\n"," ").strip() for c in row] for row in table if row]
            if not rows: continue
            width=max(len(r) for r in rows)
            rows=[r+[""]*(width-len(r)) for r in rows]
            md=["| "+" | ".join(rows[0])+" |", "| "+" | ".join(["---"]*width)+" |"]
            md += ["| "+" | ".join(r)+" |" for r in rows[1:]]
            output.append("\n".join(md))
    return output
