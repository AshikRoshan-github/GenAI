from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI  
from langchain.chains import create_extraction_chain


loader = AsyncChromiumLoader(["https://www.gadgets360.com/mobile-recharge-plans/airtel-prepaid"])

html = loader.load()
bs_transformer = BeautifulSoupTransformer()
docs_transformed = bs_transformer.transform_documents(html, tags_to_extract=["tr"])

splitter=RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=0)
splits = splitter.split_documents(docs_transformed)

schema = {
    "properties": {
        "Airtel Recharge Plans": {"type": "string","description": "from the given text content, drag the airtel recharge plans.Example:₹29 for 1 Day 2GB Data Pack,₹49 for 1 Day NA Data Pack, Unlimited, Unlimited Talktime and 1.5GB/Day Data For 84 Days @₹719 Pack,etc."},
        "Data": {"type": "string","description":"from the given text content, drag the data.Example:1GB,1.5GB Per Day,etc."},
        "Validity": {"type": "string","description":"from the given text content, drag the validity.Example:1Day,EXISTING PLAN,etc."},
        "Price":{"type":"string","description":"from the given text content, drag the price.Example:₹29,₹549,etc."}

    },
    "required": ["Airtel Recharge Plans","Data","Validity","Price"],
}

#llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613", openai_api_key="xxxxxxx")

def extract(content: str, schema: dict):
    return create_extraction_chain(schema=schema, llm=llm).run(content)

extracted_content = extract(schema=schema, content=splits[0].page_content)

print(extracted_content)
