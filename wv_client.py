import weaviate
from langchain_community.embeddings import HuggingFaceEmbeddings
import json
import weaviate.classes.config as wc
embeddings = HuggingFaceEmbeddings()
def get_metadata():
    with open('split/split_papers_6.json', 'r') as f:
        for line in f:
            yield line
def generate_embeddings(string):
    embed = embeddings.embed_query(string)
    return embed
client = weaviate.connect_to_wcs(
    cluster_url='https://genai-project-79dbyswn.weaviate.network',  # Replace with your WCS URL
    auth_credentials=weaviate.auth.AuthApiKey("hMbfwskImMEhtIZPwBsEqTCHfnN3TaAsIcaq"),
    skip_init_checks=True  # Replace with your WCS key
    )  # Use this context manager to ensure the connection is closed
print('is_ready:', client.is_ready())
# if client.collections.exists("arxiv"):
#     client.collections.delete("arxiv")
# client.collections.create(
#     name="arxiv",
#      properties=[
#                 wc.Property(name="paper_id", data_type=wc.DataType.TEXT),
#                 wc.Property(name="paper_authors", data_type=wc.DataType.TEXT),
#                 wc.Property(name="paper_title", data_type=wc.DataType.TEXT),
#                 wc.Property(name="paper_doi", data_type=wc.DataType.TEXT),
#                 wc.Property(name="paper_abstract", data_type=wc.DataType.TEXT),
#                 wc.Property(name="paper_update_date", data_type=wc.DataType.TEXT),
#             ],
#             # Define the vectorizer module (none, as we will add our own vectors)
#             vectorizer_config=wc.Configure.Vectorizer.none(),
# )
 
try:
    count = 1000
    metadata = get_metadata()
    collection = client.collections.get("arxiv")
    with collection.batch.fixed_size(batch_size=500, concurrent_requests=1000) as batch: 
        for i, paper in enumerate(metadata):
            lib = {}
            for k, v in json.loads(paper).items():
        # print(f'{k}: {v}')
                if k in ['id', 'authors', 'title', 'doi', 'abstract', 'update_date']:
                    lib['paper_'+k] = v
            
            vec = generate_embeddings(lib['paper_title']+lib['paper_abstract'])
            batch.add_object(
                    properties=lib,
                    vector=vec
            )
            if(i%1000 == 0):
                print(i)
            # print(i, collection.batch.failed_objects,  collection.batch.failed_references )
           

finally:
    client.close()