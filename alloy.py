import bs4
from langchain_google_vertexai import ChatVertexAI
from langchain_google_alloydb_pg import AlloyDBEngine, AlloyDBVectorStore, AlloyDBLoader
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

engine = AlloyDBEngine.from_instance(
    region="us-east4",
    cluster="julietest",
    instance="julietest",
    database="julietest",
    user="postgres",
    password=" julietest",
)

try:
    engine.init_vectorstore_table(table_name="julietest", vector_size=768)
except:
    pass

embeddings_service = VertexAIEmbeddings(model_name="textembedding-gecko@003")
vectorstore = AlloyDBVectorStore.create_sync(
    engine,
    table_name="julietest",
    embedding_service=embeddings_service
)



bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs={"parse_only": bs4_strainer},
)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                               chunk_overlap=200,
                                               add_start_index=True)

splits = text_splitter.split_documents(docs)

vectorstore = vectorstore.add_documents(
        engine=engine,
        table_name="julietest",
        documents=splits,
        embedding=embeddings_service,
)


# Retrieve and generate using the relevant snippets of the blog.
retriever = vectorstore.as_retriever()

prompt = hub.pull("rlm/rag-prompt")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


llm = ChatVertexAI(model="gemini-pro")

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

output = rag_chain.invoke("What is Task Decomposition?")
print(output)
