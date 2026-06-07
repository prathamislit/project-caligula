"""SEC EDGAR filing index logic."""

from .sec_fetch import get_submissions


def get_filing_index(cik: str, form_type: str):
    """Retrieve index of specific SEC filings for a given CIK."""
    subs = get_submissions(cik)
    recent = subs.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accs = recent.get("accessionNumber", [])
    docs = recent.get("primaryDocument", [])

    out = []
    for i, f in enumerate(forms):
        if f == form_type:
            out.append(
                {
                    "accession": accs[i],
                    "date": dates[i],
                    "document": docs[i],
                }
            )
    return out
