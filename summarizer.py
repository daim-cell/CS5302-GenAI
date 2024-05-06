import os
import PyPDF2
import re
import openai
from config import OPEN_AI_KEY, PICK_PAPERS_TO_SUMMARIZE


openai.api_key = OPEN_AI_KEY

def call_summarizer(scrapped_papers):
    summarized_papers = []
    # ADDED TO AVOID OVERUSE OF API
    scrapped_papers = scrapped_papers[:len(scrapped_papers)]
    for i,scrapped_paper in enumerate(scrapped_papers):
        scrapped_content = scrapped_paper['scrapped_content']
        scrapped_url = scrapped_paper['url']
        scrapped_pid = scrapped_paper['pid']

        pdf_summary_text = ""
        # Open the PDF file
        # pdf_file_path = "sample_data/paper_6pages.pdf"
        # # Read the PDF file using PyPDF2
        # pdf_file = open(pdf_file_path, 'rb')
        # pdf_reader = PyPDF2.PdfReader(pdf_file)
 
        client = openai.OpenAI(api_key=openai.api_key) 
        # client = OpenAI()
        # response = client.chat.completions.create(
        #   model="gpt-3.5-turbo-0125",
        #   response_format={ "type": "json_object" },
        #   messages=[
        #     {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
        #     {"role": "user", "content": "Who won the world series in 2020?"}
        #   ]
        # )
        # print(response.choices[0].message.content)
 
 
        try:
            prompt = [ {"role": "system", "content": "You are a helpful research assistant specializing in summarization, your objective is to generate concise versions of the user's query."},{"role": "user", "content": f"Summarize this: {scrapped_content}"}]
            model = "gpt-3.5-turbo"
            response = client.chat.completions.create(
                            model= model,
                            messages= prompt,
                            temperature = 0.0 )
    
            summarized_content = response.choices[0].message.content #response["choices"][0]["message"]["content"]
            # print(summarized_content)
            # pdf_summary_text+=summarized_content + "\n"
            # pdf_summary_file = pdf_file_path.replace(os.path.splitext(pdf_file_path)[1], "_summary.txt")
            # with open(pdf_summary_file, "w+") as file:
            #     file.write(pdf_summary_text)

            # pdf_file.close()
            summarized_file_name = "summarized/"+scrapped_pid+"_summarized.txt"
            with open(summarized_file_name, "w+", encoding='utf-8') as file:
                file.write(summarized_content)
                print("summarized https://arxiv.org/pdf/" +scrapped_pid+ ".pdf "+ summarized_file_name +" - "+str(i+1)+"/"+str(len(scrapped_papers))+", summarized-word-count = "+str(len(summarized_content.split(" "))) +" vs scrapped-content-count = "+ str(len(scrapped_content.split(" ")))+ " ...")
                summarized_papers.append({"pid":scrapped_pid, "url":scrapped_url, "summarized_content": summarized_content})        
            # summarized_file_name.close()
        
        except Exception as e: 
            print(f"an error occurred while summarizing https://arxiv.org/pdf/{scrapped_pid}.pdf: {str(e)}")
        
        # Loop through all the pages in the PDF file
        # for page_num in range(len(pdf_reader.pages)):
        #     # Extract the text from the page
        #     page_text = pdf_reader.pages[page_num].extract_text().lower()

        #     prompt = [ {"role": "system", "content": "You are a helpful research assistant."},{"role": "user", "content": f"Summarize this: {page_text}"}]
        #     model = "gpt-3.5-turbo"
        #     response = client.chat.completions.create(
        #                     model= model,
        #                     messages= prompt,
        #                     temperature = 0.0 )

        #     response.choices[0].message.content
        #     page_summary = response.choices[0].message.content #response["choices"][0]["message"]["content"]
        #     print(page_summary)
        #     pdf_summary_text+=page_summary + "\n"
        #     pdf_summary_file = pdf_file_path.replace(os.path.splitext(pdf_file_path)[1], "_summary.txt")
        #     with open(pdf_summary_file, "w+") as file:
        #         file.write(pdf_summary_text)

        # pdf_file.close()

        # with open(pdf_summary_file, "r") as file:
        #     print(file.read())

    return summarized_papers