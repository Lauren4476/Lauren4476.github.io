#!/usr/bin/env python
# coding: utf-8

# # Publications markdown generator for academicpages
# 
# Takes a set of bibtex of publications and converts them for use with [academicpages.github.io](academicpages.github.io). This is an interactive Jupyter notebook ([see more info here](http://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/what_is_jupyter.html)). 
# 
# The core python code is also in `pubsFromBibs.py`. 
# Run either from the `markdown_generator` folder after replacing updating the publist dictionary with:
# * bib file names
# * specific venue keys based on your bib file preferences
# * any specific pre-text for specific files
# * Collection Name (future feature)
# 
# TODO: Make this work with other databases of citations, 
# TODO: Merge this with the existing TSV parsing solution


from pybtex.database.input import bibtex
import pybtex.database.input.bibtex 
from time import strptime
import string
import html
import os
import re
import urllib.parse

def clean_abstract_text(text):
    """Strip common LaTeX artifacts (braces, escaped symbols, a few math macros)
    left over in abstracts pulled from ADS/Zotero bibtex exports."""
    text = str(text)
    text = text.replace("\\$", "\u0001")  # protect literal escaped dollar signs
    replacements = {
        "{": "", "}": "",
        "\\&": "&", "\\%": "%", "\\_": "_",
        "\\sim": "~", "\\times": "x",
        "\\lesssim": "≲", "\\lessequivlnt": "≲", "\\gtrsim": "≳",
        "\\approx": "≈", "\\pm": "±",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace("$", "")  # drop remaining math-mode delimiters
    text = text.replace("\u0001", "$")  # restore literal dollar signs
    return html_escape(text)


_ACCENTS = {
    "'": {"a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú", "y": "ý",
          "A": "Á", "E": "É", "I": "Í", "O": "Ó", "U": "Ú"},
    "`": {"a": "à", "e": "è", "i": "ì", "o": "ò", "u": "ù",
          "A": "À", "E": "È", "I": "Ì", "O": "Ò", "U": "Ù"},
    '"': {"a": "ä", "e": "ë", "i": "ï", "o": "ö", "u": "ü",
          "A": "Ä", "E": "Ë", "I": "Ï", "O": "Ö", "U": "Ü"},
    "^": {"a": "â", "e": "ê", "i": "î", "o": "ô", "u": "û",
          "A": "Â", "E": "Ê", "I": "Î", "O": "Ô", "U": "Û"},
    "~": {"n": "ñ", "o": "õ", "a": "ã", "N": "Ñ", "O": "Õ", "A": "Ã"},
    "c": {"c": "ç", "C": "Ç"},
    "v": {"c": "č", "s": "š", "z": "ž", "C": "Č", "S": "Š", "Z": "Ž"},
    "H": {"o": "ő", "u": "ű", "O": "Ő", "U": "Ű"},
}


def clean_latex_name(text):
    """Convert a LaTeX-escaped bibtex name fragment (e.g. from an ADS/Zotero
    export) into plain unicode, e.g. "{\\relax Th}" -> "Th", "Cort{\\'e}s" -> "Cortés"."""
    text = str(text)
    text = re.sub(r"\\relax\s*", "", text)

    def repl_accent(m):
        cmd, ch = m.group(1), m.group(2)
        return _ACCENTS.get(cmd, {}).get(ch, ch)

    text = re.sub(r"\\([\'`\"^~cvH])\{?([a-zA-Z])\}?", repl_accent, text)
    text = text.replace("\\o", "ø").replace("\\O", "Ø")
    text = text.replace("\\ss", "ß").replace("\\aa", "å").replace("\\AA", "Å")
    text = text.replace("\\&", "&")
    text = html.unescape(text)
    text = text.replace("{", "").replace("}", "")
    return text.strip()


def get_ads_url(b, clean_title):
    """Build a link to the paper's ADS abstract page.

    Prefers the ADS bibcode (Zotero stores this in the 'annotation' field
    when items are imported from ADS), then falls back to the DOI, and
    finally to an ADS title search if neither is available.
    """
    if "annotation" in b:
        m = re.search(r"ADS Bibcode:\s*([^\s,}]+)", str(b["annotation"]))
        if m:
            bibcode = m.group(1).replace("\\&", "&")
            return "https://ui.adsabs.harvard.edu/abs/" + urllib.parse.quote(bibcode, safe="") + "/abstract"
    if "doi" in b and len(str(b["doi"])) > 3:
        return "https://ui.adsabs.harvard.edu/abs/" + urllib.parse.quote(str(b["doi"]), safe="") + "/abstract"
    return "https://ui.adsabs.harvard.edu/search/q=title%3A%22" + urllib.parse.quote(clean_title.replace("-", " ")) + "%22"


def get_arxiv_id(b):
    """Find the paper's arXiv identifier.

    Uses the 'eprint' field from an ADS bibtex export if present, otherwise
    looks for an "arXiv: 2602.17177" line in the Zotero 'Extra' field
    (exported as 'annotation'). Returns None if neither is available.
    """
    if "eprint" in b and len(str(b["eprint"])) > 3:
        return str(b["eprint"]).replace("arXiv:", "").strip()
    if "annotation" in b:
        m = re.search(r"arXiv:\s*([^\s,}]+)", str(b["annotation"]))
        if m:
            return m.group(1)
    return None

#todo: incorporate different collection types rather than a catch all publications, requires other changes to template
publist = {
    "proceeding": {
        "file" : "my_proceedings.bib",
        "venuekey": "booktitle",
        "venue-pretext": "In the proceedings of ",
        "collection" : {"name":"publications",
                        "permalink":"/publication/"}
        
    },
    "journal":{
        "file": "my_publications.bib",
        "venuekey" : "journal",
        "venue-pretext" : "",
        "collection" : {"name":"publications",
                        "permalink":"/publication/"}
    } 
}

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;"
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)


os.makedirs("../_publications", exist_ok=True)

os.makedirs(os.path.join("..", "_publications"), exist_ok=True)

for pubsource in publist:
    parser = bibtex.Parser()
    bibdata = parser.parse_file(publist[pubsource]["file"])

    #loop through the individual references in a given bibtex file
    for bib_id in bibdata.entries:
        #reset default date
        pub_year = "1900"
        pub_month = "01"
        pub_day = "01"
        
        b = bibdata.entries[bib_id].fields
        
        try:
            pub_year = f'{b["year"]}'

            #todo: this hack for month and day needs some cleanup
            if "month" in b.keys(): 
                if(len(b["month"])<3):
                    pub_month = "0"+b["month"]
                    pub_month = pub_month[-2:]
                elif(b["month"] not in range(12)):
                    tmnth = strptime(b["month"][:3],'%b').tm_mon   
                    pub_month = "{:02d}".format(tmnth) 
                else:
                    pub_month = str(b["month"])
            if "day" in b.keys(): 
                pub_day = str(b["day"])

                
            pub_date = pub_year+"-"+pub_month+"-"+pub_day
            
            #strip out {} as needed (some bibtex entries that maintain formatting)
            clean_title = b["title"].replace("{", "").replace("}","").replace("\\","").replace(" ","-")    

            url_slug = re.sub("\\[.*\\]|[^a-zA-Z0-9_-]", "", clean_title)
            url_slug = url_slug.replace("--","-")

            md_filename = (str(pub_date) + "-" + url_slug + ".md").replace("--","-")
            html_filename = (str(pub_date) + "-" + url_slug).replace("--","-")

            #Build Citation from text
            citation = ""
            authors = bibdata.entries[bib_id].persons["author"]

            #citation authors - todo - add highlighting for primary author?
            author_names = []
            for author in authors:
                first = clean_latex_name(author.first_names[0]) if author.first_names else ""
                last = clean_latex_name(author.last_names[0])
                citation = citation+" "+(first+" "+last).strip()+", "
                author_names.append((first+" "+last).strip())

            #short "A. Author, B. Author, C. Author et al. YEAR" citation for the top of the page
            short_parts = []
            for author in authors[:3]:
                first = clean_latex_name(author.first_names[0]) if author.first_names else ""
                last = clean_latex_name(author.last_names[0])
                initial = (first[0] + ".") if first else ""
                short_parts.append((initial + " " + last).strip())
            if len(authors) > 3:
                citation_short = ", ".join(short_parts) + " et al. " + pub_year
            else:
                citation_short = ", ".join(short_parts) + " " + pub_year

            #citation title
            citation = citation + "\"" + html_escape(b["title"].replace("{", "").replace("}","").replace("\\","")) + ".\""

            #add venue logic depending on citation type
            venue = publist[pubsource]["venue-pretext"]+b[publist[pubsource]["venuekey"]].replace("{", "").replace("}","").replace("\\","")

            citation = citation + " " + html_escape(venue)
            citation = citation + ", " + pub_year + "."

            
            ## YAML variables
            md = "---\ntitle: \""   + html_escape(b["title"].replace("{", "").replace("}","").replace("\\","")) + '"\n'
            
            md += """collection: """ +  publist[pubsource]["collection"]["name"]

            md += """\npermalink: """ + publist[pubsource]["collection"]["permalink"]  + html_filename
            
            note = False
            if "note" in b.keys():
                if len(str(b["note"])) > 5:
                    md += "\nexcerpt: '" + html_escape(b["note"]) + "'"
                    note = True

            abstract = False
            if "abstract" in b.keys():
                if len(str(b["abstract"])) > 5:
                    print("Cleaning abstract for entry: ", bib_id)
                    clean_abstract = clean_abstract_text(b["abstract"])
                    abstract = True

            md += "\ndate: " + str(pub_date) 

            md += "\nvenue: '" + html_escape(venue) + "'"

            if "volume" in b.keys():
                md += "\nvolume: '" + html_escape(str(b["volume"])) + "'"

            if "pages" in b.keys():
                md += "\npages: '" + html_escape(str(b["pages"])) + "'"

            md += "\nauthors: '" + html_escape(", ".join(author_names)) + "'"

            if "doi" in b.keys() and len(str(b["doi"])) > 3:
                md += "\ndoi: '" + str(b["doi"]) + "'"

            arxiv_id = get_arxiv_id(b)
            if arxiv_id:
                md += "\narxiv: '" + arxiv_id + "'"

            url = False
            if "url" in b.keys():
                if len(str(b["url"])) > 5:
                    md += "\npaperurl: '" + b["url"] + "'"
                    url = True

            md += "\ncitation_short: '" + html_escape(citation_short) + "'"

            md += "\nadsurl: '" + get_ads_url(b, clean_title) + "'"

            md += "\ncitation: '" + html_escape(citation) + "'"

            md += "\n---"

            
            ## Markdown description for individual page
            if note:
                md += "\n" + html_escape(b["note"]) + "\n"

            if abstract:
                md += "\n**Abstract**\n\n" + clean_abstract + "\n"

            if url:
                md += "\n[Access paper here](" + b["url"] + "){:target=\"_blank\"}\n"

            md_filename = os.path.basename(md_filename)
            out_path = os.path.abspath(os.path.join("..", "_publications", md_filename))

            with open(out_path, 'w', encoding="utf-8") as f:
                f.write(md)
            print(f'SUCCESSFULLY PARSED {bib_id}: \"', b["title"][:60],"..."*(len(b['title'])>60),"\"")
            print(f'  -> wrote to: {out_path}')
        # field may not exist for a reference
        except KeyError as e:
            title_preview = str(b["title"])[:30] + ("..." if len(str(b.get("title", ""))) > 30 else "") if "title" in b else "(no title field found)"
            print(f'WARNING Missing Expected Field {e} from entry {bib_id}: "{title_preview}" -- available fields: {list(b.keys())}')
            continue