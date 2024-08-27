import openai
from dotenv import load_dotenv
from langchain_teddynote import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings, AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

# API 키 정보 로드
load_dotenv()

# 프로젝트 초기 설정
def initialize_project():
    logging.langsmith("CH12-RAG")

# 문서 로드 함수
def load_documents():
    # CSV 문서 로드
    loader_csv = DirectoryLoader(
        "../data/대출사기형/csv",
        glob="*.csv",
        loader_cls=CSVLoader, loader_kwargs={"encoding": "utf-8"}
    )
    # PDF 문서 로드
    loader_pdf = PyMuPDFLoader("(교재)안전한 금융생활을 위한 보이스피싱 대처 방법.pdf")
    # loader_pdf = DirectoryLoader(
#     "./(교재)안전한 금융생활을 위한 보이스피싱 대처 방법.pdf",
#     glob="*.pdf",
#     loader_cls=PyMuPDFLoader,
#     )
    
    document_csv = loader_csv.load()
    document_pdf = loader_pdf.load()
    
    return document_csv, document_pdf

# 문서 변환 함수
def file_to_retriever(doc, text_splitter, embeddings):
    split_documents = text_splitter.split_documents(doc)
    vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)
    retriever = vectorstore.as_retriever()
    return retriever

# 체인 생성 함수
def create_chain(retriever, prompt, llm):
    chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    return chain

# 메인 함수
def main():
    initialize_project()
    
    document_csv, document_pdf = load_documents()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    embeddings = HuggingFaceEmbeddings(model_name="jhgan/ko-sroberta-multitask")
    llm = AzureChatOpenAI(deployment_name="gpt-4o",)
    
    retriever_csv = file_to_retriever(document_csv, text_splitter, embeddings)
    retriever_pdf = file_to_retriever(document_pdf, text_splitter, embeddings)
    
    # 프롬프트 설정
    prompt = PromptTemplate.from_template(
        """You are an assistant for summarization tasks. 
        following pieces of retrieved context is example of similar context. catch the keyword it to answer the question if exists. 
        summarize the conversation transparently. don't judge anything. 
        Answer in Korean.

        #Question: 
        {question} 
        #Context: 
        {context} 

        #Answer:"""
    )

    prompt1 = PromptTemplate.from_template(
        """You are an assistant for fraud detection tasks. 
        Use the following pieces of retrieved context to answer the question. 
        Label and reason message from a user with an intent whether to fraud or not. advertising is not fraud.
        Answer in Korean.

        #Question: 
        {question} 
        #Context: 
        {context} 

        #Answer:"""
    )
    
    first_chain = create_chain(retriever_csv, prompt, llm)
    second_chain = create_chain(retriever_pdf, prompt1, llm)
    
    question = """A : 본인 성함 알겟습니다. 제가 첫번째는 이제 본인이 혹시라도 이제 깡통 계좌 발생으로 해서 본인이 금전적인 피해를 보네 보신 게 있는지에 대해서 제가 확인을 해봐야 되겠구요
    B : 네
    A : 아 아 그 두번째 같은 경우는 혹시라도 본인이 이 자금을 어 이제 조사를 피하기 위해서 어 다른 계좌로 돈을 바로 이체를 하는 게 아니냐 예를 들어서 깡통 계좌가 발생하더라도 앞으로는 제가 계좌 쪽을 조사를 진행을 해야 되는데 깡통 계좌가 갑자기 이자 발생을 하면 아예 이제 (삐-) 씨가 당황스럽고 피해를 봤다고 생각을 할 거에요. 그냥 저희 입장에서 봤을 때는 혹시 제가 (삐-) 계좌 추적을 피하기 위해서 한번 받고 하면 네 그분한테 계좌 이체를 시도를 한 게 아니냐 그러면 절차가 조금 더 복잡해줄 수 있어요. 계좌 발생하면.
    B : 네 네
    A : 아 그래서 깡통 계좌 내용에 대한 거는 이제 실질적으로 제가 설명드렸듯이 이 계좌 잔고가 얼마가 있던 상관 없습니다. 돈이 액수가 필요한게 아니고
    B : 네 예
    A : 한번 확인을 해도 출금 시도를 해봐야 진짜로 내가 원하는 만큼 돈이 출금이 되냐를 제가 확인할 수가 있다는 거예요. 출금을 했을때 진짜 본인이 원하는 대로 돈이 나오지 않았을 경우 당사자가 실질적으로 내가 어 이게 깡통 계좌구나하고 그때 좀 더 빼드릴 수가 있다는 겁니다. 아 그쵸 그래서 어 한번 좀 확인해봐야 되는 거는 본인이 직접적으로 이제 농협 은행권에 잠시 뒤 방문을 해줘야 될 것 같은데, 어 이거는 제가 그렇다고 제가 통장을 가지고 제가 가서 뭐 돈을 찾을 수 없잖아요
    B : 네 그렇죠
    A : 말이 안 돼 예 말이 안 됐기 때문에 본인이 직접적으로 이동을 해줘 갖고 일단은 뭐 은행권으로 방문을 하는 데 있어서 뭐 번거로움이 있을 거 같애요
    B : 아니요 내일 방문 하면 될 것 같은데요
    A : 내일이요?
    B : 네
    """
    
    summary = first_chain.invoke(question)
    print(summary)

    result = second_chain.invoke(summary)
    print(result)

if __name__ == "__main__":
    main()
