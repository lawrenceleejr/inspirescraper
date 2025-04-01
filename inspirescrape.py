import requests
import re


published_count = 0
preprint_count = 0

def get_inspire_articles(author_id,page=1):
    base_url = "https://inspirehep.net/api/literature"
    params = {
        "q": f"author:{author_id}",
        "sort": "mostrecent",
        "size": 50,  # Adjust this if needed
        "page": page
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()

def convert_latex_to_unicode(text):
    # Remove LaTeX math delimiters
    text = text.replace("$", "")
    
    # Extensive replacements for Greek letters and common LaTeX symbols
    replacements = {
        r"\\alpha": "α", r"\\beta": "β", r"\\gamma": "γ", r"\\delta": "δ",
        r"\\epsilon": "ε", r"\\zeta": "ζ", r"\\eta": "η", r"\\theta": "θ",
        r"\\iota": "ι", r"\\kappa": "κ", r"\\lambda": "λ", r"\\mu": "μ",
        r"\\nu": "ν", r"\\xi": "ξ", r"\\omicron": "ο", r"\\pi": "π",
        r"\\rho": "ρ", r"\\sigma": "σ", r"\\tau": "τ", r"\\upsilon": "υ",
        r"\\phi": "φ", r"\\chi": "χ", r"\\psi": "ψ", r"\\omega": "ω",
        r"\\Gamma": "Γ", r"\\Delta": "Δ", r"\\Theta": "Θ", r"\\Lambda": "Λ",
        r"\\Xi": "Ξ", r"\\Pi": "Π", r"\\Sigma": "Σ", r"\\Upsilon": "Υ",
        r"\\Phi": "Φ", r"\\Psi": "Ψ", r"\\Omega": "Ω",
        r"\\times": "×", r"\\leq": "≤", r"\\geq": "≥", r"\\neq": "≠",
        r"\\infty": "∞", r"\\sqrt": "√", r"\\sum": "∑", r"\\int": "∫",
        r"\\to": "→"
    }
    for latex, unicode_char in replacements.items():
        text = re.sub(latex, unicode_char, text)
    
    # Remove remaining LaTeX commands and markup (e.g., \textbf{X} -> X, \textrm{X} -> X, <markup> -> )
    text = re.sub(r"\\[a-zA-Z]+\{(.*?)\}", r"\1", text)
    text = re.sub(r"~", " ", text)  # Remove LaTeX tildes (non-breaking spaces)
    text = re.sub(r"[{}]", "", text)  # Remove LaTeX curly brackets
    text = re.sub(r"<.*?>", "", text)  # Remove any markup tags
    text = re.sub(r"\\", "", text)  # Remove unexplained backslashes
    text = re.sub(r"\^|_", "", text)  # Remove LaTeX superscript and subscript symbols
    text = re.sub(r"textrm", "", text)  # Remove LaTeX superscript and subscript symbols
    return text

def format_bibliography(entries):
    published_bibliography = []
    preprint_bibliography = []
    global published_count
    global preprint_count
    
    for entry in entries:
        title = entry.get("metadata", {}).get("titles", [{}])[0].get("title", "Unknown Title")
        title = convert_latex_to_unicode(title)
        
        authors = entry.get("metadata", {}).get("authors", [])
        collaboration = entry.get("metadata", {}).get("collaborations", [{}])[0].get("value", "")
        
        if collaboration:
            author_list = f"{collaboration} Collaboration"
        elif len(authors) > 200:
            author_list = "Large Collaboration"
        elif len(authors) > 3:
            author_list = ", ".join(a.get("full_name", "") for a in authors[:3]) + ", et al."
        else:
            author_list = ", ".join(a.get("full_name", "") for a in authors)
        
        publication_info = entry.get("metadata", {}).get("publication_info", [{}])[0]
        journal_title = publication_info.get("journal_title", "")
        volume = publication_info.get("journal_volume", "")
        issue = publication_info.get("journal_issue", "")
        pages = publication_info.get("page_start", "")
        year = entry.get("metadata", {}).get("earliest_date", "Unknown Year").split("-")[0]
        
        if volume:
            journal_ref = f"{journal_title}, {volume}"
            if issue:
                journal_ref += f", ({issue})"
            if pages:
                journal_ref += f", {pages}"
        else:
            journal_ref = journal_title
        
        arxiv_id = entry.get("metadata", {}).get("arxiv_eprints", [{}])[0].get("value", "")
        inspire_id = entry.get("id", "")
        link = f"https://inspirehep.net/literature/{inspire_id}"
        
        if journal_title:
            published_count += 1
            entry_text = f"{published_count}. {author_list} {year}, {title}, {journal_ref}, [arXiv:{arxiv_id}], ({link})"
            published_bibliography.append(entry_text)
            print(f"Processing Published {published_count}: {title}")
        else:
            preprint_count += 1
            entry_text = f"{preprint_count}. {author_list} {year}, {title}, [arXiv:{arxiv_id}], ({link})"
            preprint_bibliography.append(entry_text)
            print(f"Processing Preprint {preprint_count}: {title}")

        print(published_count, len(published_bibliography))
        print(preprint_count, len(preprint_bibliography))
    
    return "\n".join(published_bibliography), "\n".join(preprint_bibliography)

def main():
    author_id = "lawrence.lee.jr.1"
    # entries = []
    # tmpentries = {}
    published_bibliography = ""
    preprint_bibliography = ""
    for page in range(1,40):
        data = get_inspire_articles(author_id,page)
        tmpentries = data.get("hits", {}).get("hits", [])
        # print(type(tmpentries))
        # print(tmpentries)
        print(len(tmpentries))
        # entries.append(tmpentries)
        # entries.append(tmpentries)

        tmppublished_bibliography, tmppreprint_bibliography = format_bibliography(tmpentries)

        published_bibliography += tmppublished_bibliography+"\n"
        preprint_bibliography += tmppreprint_bibliography+"\n"

    with open("published_bibliography.txt", "w", encoding="utf-8") as f:
        f.write(published_bibliography)
    
    with open("preprint.txt", "w", encoding="utf-8") as f:
        f.write(preprint_bibliography)
    
    print("Bibliographies saved to published_bibliography.txt and preprint.txt")

if __name__ == "__main__":
    main()