**apify_qa.py :**


The Python code uses Langchain, Apify, and a vector database to answer questions based on crawled website content. Here's a breakdown of the architecture:

1. Environment Setup:

Process: Sets environment variables for OpenAI and Apify API keys. These are necessary for authenticating with the respective services.

2. Website Crawling (Apify):

Input: A starting URL (https://www.gadgets360.com/mobile-recharge-plans/airtel-prepaid) is provided as input to the Apify website-content-crawler actor.

Process: The ApifyWrapper is used to call the Apify actor. The actor crawls the given URL and extracts text content from the web page(s). A dataset_mapping_function transforms the crawled data into Langchain Document objects, storing the page content and the source URL as metadata.

Output: A Langchain DocumentLoader object (specifically, an instance of ApifyDatasetLoader which is returned by call_actor) containing the crawled website content as a list of Document objects.

3. Index Creation (Langchain):

Input: The DocumentLoader from the previous step.

Process:

VectorstoreIndexCreator creates a vector database index. It takes the DocumentLoader as input.

Behind the scenes, this involves:

Splitting the documents into chunks if needed.

Creating embeddings (vector representations) of the text chunks using a language model (likely backed by OpenAI, as indicated by the API key).

Storing these embeddings and the associated text chunks in a vector database.

Output: A VectorStore index object. This object allows efficient similarity searches.

4. Querying (Langchain):

Input: A user query ("What is airtel recharge plan available?").

Process:

The query_with_sources method of the index is called with the user query.

The query is embedded (converted into a vector) using the same language model as in step 3.

The vector database performs a similarity search to find the most relevant text chunks based on the query embedding.

The relevant chunks, along with their source URLs (from the metadata), are retrieved.

Output: A dictionary containing the answer and the sources used to generate the answer.

5. Print Results:

Input: The dictionary returned from the query.

Process: The code prints the generated answer and the source URLs to the console.

Architecture Diagram:

                 +----------------+    +------------------+    +--------------+    +-----------+
                 | Crawl Website  |--->| Create Vector    |--->| Query Index |--->| Print     |
                 | (Apify)       |    | DB Index        |    |            |    | Results   |
                            | (Langchain)      |    |            |    +-----------+
                 |                |    |                  |    +--------------+
                 |  Output:       |    |  Output:         |       Input: Query,
                 |  DocumentLoader|    |  VectorStore     |
                 +----------------+    +------------------+

**web_data_extractor.py**:

The code performs structured information extraction from a web page using Langchain, Beautiful Soup, and an LLM (likely OpenAI's GPT). Here's an architectural breakdown:

1. Web Page Loading:

Input: A URL (https://www.gadgets360.com/mobile-recharge-plans/airtel-prepaid).

Process: AsyncChromiumLoader loads the web page content using a headless browser. This allows it to handle dynamically loaded content.

Output: A list of Document objects, each containing the HTML content of the loaded page. In this case, it's likely a single Document as only one URL is provided.

2. HTML Parsing and Tag Extraction:

Input: The list of Document objects from the previous step.

Process: BeautifulSoupTransformer parses the HTML content and extracts specific tags. Here, it's configured to extract <tr> (table row) tags, likely to target the table containing recharge plan information.

Output: A list of Document objects, now containing only the extracted <tr> tags' content.

3. Text Splitting:

Input: The transformed Document objects (containing <tr> tag content).

Process: RecursiveCharacterTextSplitter splits the extracted HTML content into smaller chunks. This is done to manage the context window limitations of the LLM. The from_tiktoken_encoder method ensures efficient splitting based on token counts.

Output: A list of Document objects, where each document represents a chunk of the original HTML content.

4. Schema Definition:

Process: A JSON schema is defined to specify the structure of the information to be extracted. The schema defines the expected fields ("Airtel Recharge Plans," "Data," "Validity," "Price") and their data types. The descriptions provide guidance to the LLM about what information should be extracted for each field.

5. Information Extraction (LLM-powered):

Input:

A chunk of HTML content ( splits[0].page_content - the first chunk from the split documents).

The defined JSON schema.

Process:

The create_extraction_chain function creates an extraction chain using the provided schema and an LLM (llm, which needs to be initialized with an appropriate LLM instance). This chain uses the LLM to extract the specified fields from the HTML chunk based on the schema's guidance.

Output: A dictionary containing the extracted information, structured according to the schema.

Architecture Diagram:

+------------+    +--------------+    +--------------+    +---------+    +-----------------+    +--------------+
| Load Web  |--->| Extract <tr> |--->| Split Text  |--->| Define  |--->| Extract Info  |--->| Extracted   |
| Page      |    | Tags        |    | Chunks      |    | Schema  |    | (LLM)       |    | Data        |
|           |    |            |    |            |    +---------+    +-----------------+    +--------------+
|           |    +--------------+    +--------------+                      |
|  Input:   |       Input: Docs      Input: Docs    |                       Input: HTML Chunk,
|    URL    |                                         |                                Schema     
+------------+                                         
