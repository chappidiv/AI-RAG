import os
import bs4 # bs4 is still useful if you want to parse the HTML before splitting
from langchain import hub
#from langchain_community.document_loaders import WebBaseLoader # Keep this for reference if you switch back
from langchain_core.documents import Document # Essential for the fix
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing import List, TypedDict
import getpass


# Import for Google Gemini Embeddings and Chat Model
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.vectorstores import InMemoryVectorStore

# --- IMPORTANT: Set USER_AGENT before any imports that might use it ---
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
# ---------------------------------------------------------------------

# Ensure GOOGLE_API_KEY is set
# It's not good practice to hardcode API keys directly in the script like this.
# The getpass.getpass() is meant to prompt the user, not be pre-filled with the key.
# If you want to set it without a prompt, simply assign it:
# os.environ["GOOGLE_API_KEY"] = ""
# However, for security, it's best to set it as a true environment variable outside the script
# or use a proper secrets management system.
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = "XXXXXXXXXXX" # Use a generic prompt

# Initialize the embedding model, explicitly passing the API key
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.environ["GOOGLE_API_KEY"])

# Initialize the vector store with the embedding model
vector_store = InMemoryVectorStore(embeddings) # Corrected back to positional argument

# Initialize the chat model, explicitly passing the API key
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.environ["GOOGLE_API_KEY"])


# --- FIX START ---
# Load content from local HTML file
with open("jobdata_file.html", "r") as file: # Added encoding for robustness
    file_content = file.read()

# Optional: Parse HTML to extract relevant text, similar to WebBaseLoader's strainer
# This helps remove boilerplate (headers, footers, navigation, etc.)
soup = bs4.BeautifulSoup(file_content, "html.parser")
# Assuming the relevant job data is within a specific tag/class.
# You'll need to inspect your 'jobdata_file.html' to find the correct selector.
# For example, if job descriptions are in <div class="job-description">...</div>
# You might do:
# text_elements = soup.find_all(class_=("job-title", "job-description", "company-name"))
# parsed_content = "\n\n".join([elem.get_text() for elem in text_elements])
# If you just want all text from the body, you could use:
parsed_content = soup.get_text() # Gets all text, might be noisy

print("\n\n\n")
print("--- Parsed Content Sample ---")
print(parsed_content[:500]) # Print a sample of the parsed content
print("--- End Sample ---")

# Create a LangChain Document object from the parsed content
# It's good practice to add some metadata, e.g., the source file name
docs = [Document(page_content=parsed_content, metadata={"source": "jobdata_file.html"})]

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# Now split_documents will receive a list of Document objects
all_splits = text_splitter.split_documents(docs)
# --- FIX END ---

# Index chunks - only add once
_ = vector_store.add_documents(documents=all_splits)

# Define prompt for question-answering
prompt = hub.pull("rlm/rag-prompt")

# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

# Define application steps
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}

def findJobsData(question):
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()
    result = graph.invoke({"question": question})
    return result['answer']


# Example usage (added for demonstration)
if __name__ == "__main__":
    # Compile application and test
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()
    question = "Find Principal Engineer Jobs in Charlotte"
    print("1")
    result = graph.invoke({"question": question})
    print(f"Question: {question}")
    print(f"Answer: {result['answer']}")