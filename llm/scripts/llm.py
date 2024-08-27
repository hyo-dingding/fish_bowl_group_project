

import pandas as pd
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
# from langchain.chat_models  import AzureChatOpenAI

from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage  # 이걸 사용해서 HumanMessage 타입으로 메시지를 감싸줍니다.
from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.messages import HumanMessage

# API 키 정보 로드
load_dotenv()

def extract_text_from_csv(file_content):
    df = pd.read_csv(file_content)
    
    # 각 행을 텍스트로 변환합니다.
    text_content = " ".join(df.apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1))
    return text_content

def initialize_project():
    # 프로젝트 초기화 작업
    pass

def file_to_retriever(doc):
    print('doc', doc)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    documents = [Document(page_content=d["text"]) for d in doc] 
    split_documents = text_splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name="jhgan/ko-sroberta-multitask")
    vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)
    retriever = vectorstore.as_retriever()
    return retriever

def create_chain(retriever, prompt_template):
    llm = AzureChatOpenAI(deployment_name="gpt-4o")

    context_docs = retriever.get_relevant_documents("text")
    context = " ".join([doc.page_content for doc in context_docs])
    
    formatted_prompt = prompt_template.format(question="이 문서에서 중요한 내용을 요약해주세요.", context=context)
    
    # HumanMessage 타입으로 메시지를 감싸줍니다.
    message = HumanMessage(content=formatted_prompt)
    
    # LLM을 호출하고 결과를 받아옵니다.
    result = llm([message])
    
    # result['choices'][0]['text'] 와 같은 인덱싱이 아닌, result.content를 사용합니다.
    return result.content
    # return result[0].content
    # # message = HumanMessage(content=formatted_prompt)
    # result = llm([HumanMessage(content=formatted_prompt)])
    # # result = llm(formatted_prompt)
    # return result['choices'][0]['text']


def process_csv(file_path):
    initialize_project()
    
    # CSV 파일을 DataFrame으로 읽기
    df = pd.read_csv(file_path)
    text_content = " ".join(df.apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1))

    retriever = file_to_retriever([{"text": text_content}])

    # # CSV에서 텍스트 추출
    # text_content = extract_text_from_csv(file_content)

    # # 텍스트를 처리하여 리트리버로 변환
    # retriever = file_to_retriever([{"text": text_content}])

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

    result = create_chain(retriever, prompt)
    return result

def process_text(file_content):
    """텍스트 파일을 처리하여 LLM에 전달"""
    initialize_project()

    # 텍스트를 처리하여 리트리버로 변환
    retriever = file_to_retriever([{"text": file_content}])

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

    result = create_chain(retriever, prompt)
    return result

