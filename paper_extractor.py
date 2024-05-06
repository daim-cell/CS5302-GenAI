import weaviate
from langchain_community.embeddings import HuggingFaceEmbeddings
import json
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.load import dumps, loads
from langchain_community.llms import HuggingFaceEndpoint
from langchain_community.document_loaders import ArxivLoader
from config import CLUSTER_URL, WEAVIATE_AUTH_KEY, HUGGINGFACEHUB_API_TOKEN, PICK_PAPERS_TO_SCRAP, QUERIES_TO_PERFORM, TOP_K_SEARCH


# Multi Query: Different Perspectives
embeddings = HuggingFaceEmbeddings()

def generate_embeddings(string):
    embed = embeddings.embed_query(string)
    return embed

def query_similar_papers(client, query_text):
    vec = generate_embeddings(query_text)
    results = client.query.near_vector(
        near_vector=vec,  # A list of floating point numbers
                limit=TOP_K_SEARCH,
    )
    return results

def reciprocal_rank_fusion(queries, collection, k=60):
    """ Reciprocal_rank_fusion that takes multiple lists of ranked documents 
        and an optional parameter k used in the RRF formula """
    
    # Initialize a dictionary to hold fused scores for each unique document
    fused_scores = {}
    for query in queries:
        if query != '' and 'query' not in query.lower():
            print(query)
            results = query_similar_papers(collection, query)
                # Iterate through each document in the list, with its rank (position in the list)
            for rank, paper in enumerate(results.objects):
                # Convert the document to a string format to use as a key (assumes documents can be serialized to JSON)
                title = dumps(paper.properties['paper_id'])
                # If the document is not yet in the fused_scores dictionary, add it with an initial score of 0
                if title not in fused_scores:
                    fused_scores[title] = 0
                fused_scores[title] += 1 / (rank + k)

    # Sort the documents based on their fused scores in descending order to get the final reranked results
    reranked_results = [
        (loads(doc), score)
        for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]
    # Return the reranked results as a list of tuples, each containing the document and its fused score
    return reranked_results


def get_queries(llm, query_text):
    template = """You are an AI language model assistant. Your task is to generate {queries} 
    different versions of the given user query to retrieve relevant documents from a vector 
    database. By generating multiple perspectives on the user query, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search.
    Provide these alternative queries separated by newlines and do not include any other text. Original question: {question}"""
    prompt_perspectives = ChatPromptTemplate.from_template(template)
    generate_queries = (
    prompt_perspectives 
    | llm 
    | StrOutputParser() 
    | (lambda x: x.split("\n"))
    )
    queries  = generate_queries.invoke({'question':query_text, 'queries': QUERIES_TO_PERFORM })
    return queries

# def get_papers(docs):
#     data =[]
#     for doc in docs:
#         data.append(ArxivLoader(query=doc['paper_id'], load_max_docs=1).load())
#     return data

def get_papers(docs): 

    if not docs:
        print("no documents provided.")
        return []

    ranked_papers = []
    # Load all papers first 
    print('\n')
    refs = []

    for index, doc in enumerate(docs):
        # print(f"loading paper {index+1}/{len(docs)} with ID {doc['paper_id']}")
        try:
            loaded_paper = ArxivLoader(query=doc[0], load_max_docs=1).load()
            if loaded_paper:
                paper_content = loaded_paper[0].page_content
                meta = loaded_paper[0].metadata
                word_count = len(paper_content.split())  # Count words by splitting the content by spaces
                page_count = loaded_paper[0].num_pages if hasattr(loaded_paper[0], 'num_pages') else 'Unknown'
                ref = {'Title': meta['Title'],'Authors': meta['Authors'], 'URL': f'https://arxiv.org/abs/{doc[0]}', 'Page Count': page_count, 'Summary': meta['Summary'].split('.')[0]}
                refs.append(ref)
                if len(ranked_papers) < PICK_PAPERS_TO_SCRAP and word_count<12000:
                    ranked_papers.append((loaded_paper, word_count, page_count, doc[0]))
                print(f"paper {index+1} loaded, https://arxiv.org/pdf/{doc[0]}.pdf, word-count: {word_count}, page-count: {page_count}, {index}/{len(docs)} ...")
            else:
                print(f"paper {index+1} https://arxiv.org/pdf/{doc[0]}.pdf, did not load properly...")
        except Exception as e:
            print(f"error loading paper {index+1} https://arxiv.org/pdf/{doc[0]}.pdf, error: {str(e)} ...")
            continue   


    if not ranked_papers:
        print("no data was loaded successfully.")
        return []
 
    # sorted_papers = sorted(data, key=lambda x: x[1])   
 
    # shortest_papers = sorted_papers[:PICK_PAPERS_TO_SCRAP]
    
    print('\n')
    for i, (paper, word_count, page_count, pid) in enumerate(ranked_papers, 1):
        print(f"selected papers {i}: https://arxiv.org/pdf/{pid}.pdf, word-count = {word_count}, page-count = {page_count}")

    # out = [paper[0] for paper, word_count, page_count, pid in shortest_papers]
    out = []
    for paper, word_count, page_count, pid in ranked_papers: 

        paper_data = {
            'paper': paper[0],  
            'word_count': word_count,
            'page_count': page_count,
            'pid': pid
        }
 
        out.append(paper_data) 

    return out, refs


# the main function where scrapper is called
def call_extractor(query_text):
    try:
        paper_content = []
        meta_data = []
        client = weaviate.connect_to_wcs(
        cluster_url = CLUSTER_URL,   
            auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_AUTH_KEY),
            skip_init_checks=True
        )
        # print('is_ready:', client.is_ready())
        collection = client.collections.get("arxiv")
        # query_text = "deep learning in natural language processing"
        llm = HuggingFaceEndpoint(repo_id = 'mistralai/Mistral-7B-Instruct-v0.2', huggingfacehub_api_token = HUGGINGFACEHUB_API_TOKEN)
        
        queries = get_queries(llm, query_text)
        ranked_ids = reciprocal_rank_fusion(queries, collection)
        papers = get_papers(ranked_ids)  
        # print("*********",papers[0].metadata)
        # print("*********",papers[0].keys())
        # print("-------------", papers[0]['pid'])
        # print("-------------", papers[0]['word_count'])
        #['Config', '__abstractmethods__', '__annotations__', '__class__', '__class_vars__', '__config__', '__custom_root_type__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__exclude_fields__', '__fields__', '__fields_set__', '__format__', '__ge__', '__get_validators__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__include_fields__', '__init__', '__init_subclass__', '__iter__', '__json_encoder__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__post_root_validators__', '__pre_root_validators__', '__pretty__', '__private_attributes__', '__reduce__', '__reduce_ex__', '__repr__', '__repr_args__', '__repr_name__', '__repr_str__', '__rich_repr__', '__schema_cache__', '__setattr__', '__setstate__', '__signature__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '__try_update_forward_refs__', '__validators__', '_abc_impl', '_calculate_keys', '_copy_and_set_values', '_decompose_class', '_enforce_dict_if_root', '_get_value', '_init_private_attributes', '_iter', '_lc_kwargs', 'construct', 'copy', 'dict', 'from_orm', 'get_lc_namespace', 'is_lc_serializable', 'json', 'lc_attributes', 'lc_id', 'lc_secrets', 'metadata', 'page_content', 'parse_file', 'parse_obj', 'parse_raw', 'schema', 'schema_json', 'to_json', 'to_json_not_implemented', 'type', 'update_forward_refs', 'validate']
        # print('\n')
        # for i, paper in enumerate(papers):   
        #     print("extracted paper https://arxiv.org/pdf/"+paper['pid']+".pdf - "+str(i)+"/"+str(len(papers))+ " ...")
            # meta_data.append(papers[i]['paper'].metadata)
            # paper_content.append(papers[i]['paper'].page_content)

        # print(len(meta_data), len(paper_content))
        # Pass this papers array to the summarize tool
        
        # print(papers[1].page_content[:400])
        # with open('outt.txt', 'w', encoding='utf-8') as f: 
        #     # print(papers[1].metadata['Title'])
        #     f.write(json.dumps(papers[1]['paper'].page_content, ensure_ascii=False))
        #     # f.write(str(papers) + '\n')
        #     # f.write(json.dumps(papers) + '\n')
        # print('___ \n')

    finally: 
        if client:
            client.close() 
            # print("SCRAPING RETURNS ",len(meta_data)," META-DATA", len(paper_content), " PAPER-CONTENT IN TOTAL")
            return papers #meta_data, paper_content
 