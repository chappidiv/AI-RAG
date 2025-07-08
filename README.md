# AI-RAG

Search Job data implementing RAG for Generative AI.
I came up with simple requirement for practicing RAG. Basically I have captured the live data from wellsfargo jobs webdata with navigating all UI and HTML data extracted with webscrapping technique and stored in file. 
Instead retrieving data from the gemini model, retrieving real time data from Jobs website and data chunked into pieces and embedded into vector database.
The Gemini LLM will generate real time data from vector database based on the given prompts.
And also used Lang Graph for orchestrating multiple tasks. In this example having single task but this helps for expending to multiple tasks.


Technologies Used:
Python
Web scrapping using BeautifulSoup
RAG (Vector Embedding & Vector Database)
Lang Graph
Gemini Model
LLM
Streamlit for UI
