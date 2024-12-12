from langchain.indexes import VectorstoreIndexCreator
from langchain_community.document_loaders.base import Document
from langchain_community.utilities import ApifyWrapper

import os

os.environ["OPENAI_API_KEY"]  = "xxxxxxxx"
os.environ["APIFY_API_TOKEN"] = "xxxxxxxx"

apify = ApifyWrapper()

loader = apify.call_actor(
    actor_id="apify/website-content-crawler",
    #run_input={"startUrls": [{"url": "https://python.langchain.com/en/latest/"}]},
    run_input={"startUrls": [{"url": "https://www.gadgets360.com/mobile-recharge-plans/airtel-prepaid"}]},
    dataset_mapping_function=lambda item: Document(
        page_content=item["text"] or "", metadata={"source": item["url"]}
    ),
)

index = VectorstoreIndexCreator().from_loaders([loader])

query = "What is airtel recharage plan available?"
result = index.query_with_sources(query)

print(result["answer"])
print(result["sources"])
