
import streamlit as st 
from langchain.schema import(SystemMessage, HumanMessage, AIMessage)
# import test_files.query as query
import paper_extractor
import scrapper
import summarizer
import generator

def init_style() -> None:
    with open('style.css') as f:
      st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True)

def init_page() -> None:
  st.set_page_config(
    page_title="AI Article-Referencing Assistant"
  )
  st.header("AI Article-Referencing Assistant")
  st.sidebar.title("Options") 
 

def init_messages() -> None:
    
  clear_button = st.sidebar.button("Clear Conversation", key="clear")
  if clear_button or "messages" not in st.session_state:
    st.session_state.messages = [
      SystemMessage(
        content="you are a helpful AI assistant. Reply your answer in markdown format."
      )
    ]

#
def get_answer(user_query):  
  # Call Query.py here
  # print(type(user_query))
  user_query =  'deep learning in natural language processing'  


  print("\n\n---------------------------------------------------------PROCESSING QUERY------------------------------------------------------------------\n\n")
  print("USER QUERY: ", user_query)

  print("\n\n---------------------------------------------------------EXTRACTING PAPERS-----------------------------------------------------------------\n\n")
  papers = paper_extractor.call_extractor(user_query)
  print("\nRECEIVED FROM EXTRACTOR => "+ str(len(papers)) +" EXTRACTED PAPERS IN TOTAL")
  extracted_paper = papers[0]['paper']
  extracted_pid = papers[0]['pid']
  extracted_metadata = extracted_paper.metadata
  extracted_page_content = extracted_paper.page_content

  print("\n\n---------------------------------------------------------SCRAPPING CONTENT-----------------------------------------------------------------\n\n")
  scrapped_papers = scrapper.call_scrapper(papers)
  print("\nRECEIVED FROM SCRAPPER => "+ str(len(scrapped_papers)) +" SCRAPPED PAPER-CONTENT IN TOTAL")
  scrapped_pid = scrapped_papers[0]['pid']
  scrapped_url = scrapped_papers[0]['url']
  scrapped_content = scrapped_papers[0]['scrapped_content']

  print("\n\n-----------------------------------------------------SUMMARIZING SCRAPPED CONTENT---------------------------------------------------------\n\n")
  summarized_papers = summarizer.call_summarizer(scrapped_papers)
  print("\nRECEIVED FROM SUMMARIZER => "+ str(len(summarized_papers)) +" SUMMARIZED PAPER/S IN TOTAL")
  summarized_pid = summarized_papers[0]['pid']
  summarized_url = summarized_papers[0]['url']
  summarized_content = summarized_papers[0]['summarized_content']
  
  print("\n\n-----------------------------------------------------SUMMARIZING SCRAPPED CONTENT---------------------------------------------------------\n\n")
  generated_response = generator.generation(summarized_papers, user_query)
  print("\nRECEIVED FROM GENERATOR => "+ generated_response)
 
  
  return summarized_url , summarized_content

def truncate_message(message_content):
    # Truncate message to 20 characters and add ellipses if longer
    return (message_content[:35] + '...') if len(message_content) > 20 else message_content

def main() -> None:
    init_page() 
    init_style()
    init_messages() 

    # st.button("🔗") 
    if user_input := st.chat_input("Input your article to get references!"):
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.spinner("Bot is typing ..."):
            answer1, answer2 = get_answer(user_input)
            # print(answer1, answer2)
            st.session_state.messages.append(AIMessage(content=[answer1,answer2])) 

    
    messages = st.session_state.get("messages", [])
    for message in messages:
        if isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(f"""<div style='color:white; background-color: rgb(128,128,128,0.5);margin-bottom:10px; padding:10px; border-radius: 5px; margin-bottom: 5px;'><h6>Answer 01: </h6>{message.content[0]}</div>
                            <div style='color:white; background-color: rgb(128,128,128,0.5);margin-bottom:10px; padding:10px; border-radius: 5px; margin-bottom: 5px;'><h6>Answer 02: </h6>{message.content[1]}</div>""", 
                            unsafe_allow_html=True)   
        elif isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)
                truncated_message = truncate_message(message.content)
                st.sidebar.markdown(
                    f"<div style='color:white; background-color: rgb(128,128,128,0.1); padding:10px; border-radius: 5px; margin-bottom: 5px;'>{truncated_message}</div>", 
                    unsafe_allow_html=True
                ) 

if __name__ == "__main__":
  main()

  