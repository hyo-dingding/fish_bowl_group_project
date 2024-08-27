import pandas as pd
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain_openai import AzureChatOpenAI
from langchain.chains import LLMChain

# 파일에서 텍스트 추출 함수
def extract_text_from_csv(file_content):
    df = pd.read_csv(file_content)
    text_content = " ".join(df.apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1))
    return text_content

# CSV 파일 처리 함수
def process_csv(file_content):
    print("Processing CSV file", file_content)
    text_content = extract_text_from_csv(file_content)
    return process_text(text_content)

# 프롬프트 설정
prompt_summarization = PromptTemplate.from_template(
    """You are an assistant for summarization tasks. You must list category and use it for answer.
    Following pieces of retrieved context is an example of similar context. Catch the keyword to answer the question if it exists. 
    Summarize the conversation transparently. Don't judge anything. PLEASE, WRITE KEYWORDS AND CATEGORY.
    Answer in Korean.

    #Question: 
    {question} 
    #Context: 
    {context} 
    #Category:
    {category}
    #Answer:"""
)

prompt_detection = PromptTemplate.from_template(
    """You are an assistant for fraud detection tasks. 
    Use the following pieces of retrieved context to answer the question. 
    Label and reason the message from a user with an intent whether it is fraud or not. Advertising is not fraud.
    Answer in Korean.

    #Question: 
    {question} 
    #Context: 
    {context} 
    #Answer:"""
)

prompt_speaker = PromptTemplate.from_template(
    """You are an assistant for discriminating two speakers using punctuation marks.  
    Label the speaker A, B. Answer in Korean. 

    #Question: 
    {question} 

    #Answer:"""
)

# 텍스트 파일 처리 함수
def process_text(file_content):
    print("Processing text file", file_content)
    
    # 문서 분할
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    documents = [Document(page_content=file_content)]
    split_documents = text_splitter.split_documents(documents)
    
    # 임베딩 생성 및 리트리버 초기화
    embeddings = HuggingFaceEmbeddings(model_name="jhgan/ko-sroberta-multitask")
    vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)
    retriever = vectorstore.as_retriever()

    # LLM 초기화
    llm = AzureChatOpenAI(deployment_name="gpt-4o")
    
    # 각 작업에 대해 체인 생성 및 실행
    summary_chain = LLMChain(llm=llm, prompt=prompt_summarization)
    detection_chain = LLMChain(llm=llm, prompt=prompt_detection)
    speaker_chain = LLMChain(llm=llm, prompt=prompt_speaker)
    
    # 각 체인에서의 결과를 가져옴
    summary_result = summary_chain.run({"context": split_documents})
    detection_result = detection_chain.run({"context": split_documents})
    speaker_result = speaker_chain.run({"context": split_documents})

    # 결과를 JSON 형태로 통합
    final_result = {
        "summary": summary_result,
        "detection": detection_result,
        "speaker_labels": speaker_result
    }
    
    return final_result

