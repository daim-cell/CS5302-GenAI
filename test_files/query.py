import weaviate
from langchain_community.embeddings import HuggingFaceEmbeddings
import json

embeddings = HuggingFaceEmbeddings()

def generate_embeddings(string):
    embed = embeddings.embed_query(string)
    return embed

def query_similar_papers(client, query_text):
    vec = generate_embeddings(query_text)
    results = client.query.near_vector(
        near_vector=vec,  # A list of floating point numbers
                limit=5,
    )
    return results

def query(query_text):
    try:
        client = weaviate.connect_to_wcs(
        cluster_url='https://genai-project-79dbyswn.weaviate.network',  # Replace with your WCS URL
            auth_credentials=weaviate.auth.AuthApiKey("hMbfwskImMEhtIZPwBsEqTCHfnN3TaAsIcaq"),
            skip_init_checks=True
        )
        collection = client.collections.get("arxiv")
        # query_text = "deep learning in natural language processing"
        results = query_similar_papers(collection, query_text)
        # print([obj.properties['paper_title'] for obj in results.objects])
        ret = []
        for result in results.objects:
            # print(f"Title: {result.properties}")
            ret.append(result.properties)
            print("******",result.properties)
            # print("---") 

    finally:
        client.close()
        return ret
