#ARXIV RESEARCH PAPER DATA:
from PyPDF2 import PdfReader
from io import BytesIO
import requests
import unicodedata
import re
import os
from transformers import GPT2Tokenizer

# returns the content of the paper
def getpaper_text(url):
    # url = "https://arxiv.org/pdf/2301.00017.pdf" 
    response = requests.get(url)
    response.raise_for_status()

    pdf_stream = BytesIO(response.content)
    pdfreader = PdfReader(pdf_stream)

    paper_text = ''
    for i, page in enumerate(pdfreader.pages):
        content = page.extract_text()
        if content:
            paper_text += content
    
    return paper_text

def clean_text(input_text):
    normalized_text = unicodedata.normalize('NFKD', input_text)
    cleaned_text = ''.join(c for c in normalized_text if unicodedata.category(c) not in ['Cc', 'Cf'])
    return cleaned_text

def extract_text_by_section(full_text, start_section, end_section):
    # Use regular expressions to allow for case-insensitive searching
    pattern = re.compile(r'{}(.*?){}'.format(re.escape(start_section), re.escape(end_section)), re.DOTALL | re.IGNORECASE)
    match = pattern.search(full_text)
    if match:
        main_text = match.group(1).strip()  # Extract the content between start and end sections
    else:
        main_text = "Section not found"
    # Find the start of the references section in a case-insensitive manner
    ref_start_idx = re.search(re.escape(end_section), full_text, re.IGNORECASE)
    if ref_start_idx:
        # Extract everything from the reference section onward
        references = full_text[ref_start_idx.start():].strip() 
    else:
        references = "References not found"
    return main_text, references

def trim_to_max_tokens(content):
    max_tokens=16384
    average_token_length=4
    # Calculate max characters allowed (a rough estimate)
    # max_characters = max_tokens / average_token_length
    max_characters = 14000
    
    # Trim the content if it exceeds the estimated max characters
    if len(content.split(" ")) > max_characters:
        return content[:max_characters]
    return content


def call_scrapper(papers):
    scrapped_papers = [] 
    for i,paper in enumerate(papers):
        paper = papers[i]['paper']
        pid = papers[i]['pid']
        url = "https://arxiv.org/pdf/"+pid+".pdf"

        paper_text = getpaper_text(url)
        cleaned_paper_text = clean_text(paper_text)
        # main_text, references_text = extract_text_by_section(cleaned_paper_text, "introduction", "references")

        if "REFERENCES" in cleaned_paper_text:
            scrapped_content = cleaned_paper_text.split("REFERENCES")[0]
        elif "references" in cleaned_paper_text:
            scrapped_content = cleaned_paper_text.split("references")[0]
        else:
            scrapped_content = cleaned_paper_text.split("REFERENCES")[0]

 
        scrapped_content = trim_to_max_tokens(scrapped_content)

        scrapped_file_id = pid
        # scrapped_file = scrapped_file_id.replace(os.path.splitext(scrapped_file_id)[1], "_scrapped.txt")
        scrapped_file_name = "scrapped/"+scrapped_file_id+"_scrapped.txt"
        with open(scrapped_file_name, "w+", encoding='utf-8') as file:
            file.write(scrapped_content)
            print("scrapped https://arxiv.org/pdf/" +pid+".pdf to "+scrapped_file_name+"- "+str(i+1)+"/"+str(len(papers))+", scrapped-word-count = "+str(len(scrapped_content.split(" "))))
        # scrapped_file_name.close()

        
        scrapped_papers.append({"pid" : pid, "url" : url, "scrapped_content" : scrapped_content})
    
    # print("Cleaned Paper text:\n", scrapped_content) 
    # print("Main Section:\n", main_text)
    # print("\nReferences:\n", references_text)
    return scrapped_papers
    