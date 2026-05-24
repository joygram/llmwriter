import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_classic.storage import LocalFileStore
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# 환경 변수를 로드합니다.

load_dotenv()

# Langchain을 활용하기 위한 설정과 RAG 설정을 진행합니다.
llm = ChatOpenAI(model='gpt-4o-mini',
    temperature=0.1,
)


## 참조 지식 래그  
loader = PyPDFLoader("guide.pdf")
pages = loader.load()  
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", "다.", ".", " ", ""],
)
docs = splitter.split_documents(pages)

## 가이드 임배딩 
cache_dir = LocalFileStore("./.cache/practice/")
embeddings = OpenAIEmbeddings()
cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)
vectorstore = FAISS.from_documents(docs, cached_embeddings)

retriever = vectorstore.as_retriever()

## 문서 생성 상태 저장
if 'state' not in st.session_state:
    st.session_state.state = "idle"

if 'doc' not in st.session_state:
    st.session_state.doc = ""

def draft_doc(question):
    draft_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            공문서 작성 전문가.
            기획문서, 보고서, 공고문 등 요구사항에 맞는 문서 작성. 
            문서는 표 포함 총 1장 

            참고 작성법: 
            {guide}
            """
        ),
        ("human", "{question}"),
    ]
    )

    chain = (
        {
            "guide": retriever,
            "question": RunnablePassthrough(),
        }
        | draft_prompt
        | llm
    )
    result = chain.invoke(question)
        
    return result.content


def revise_doc(current_doc, question):
    revise_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            공문서 수정 전문가.
            기존 문서 형식을 유지하되, 사용자의 수정 요청을 우선 반영한다.
            수정 요청에 포함된 명칭, 역할, 표현 변경은 반드시 결과 문서에 직접 반영한다.
            수정 요청과 충돌하지 않는 범위에서만 참고 가이드를 활용한다.
            """
        ),
        (
            "human",
            """
기존 문서:
{draft}

수정 요청:
{question}

참고 작성법:
{guide}

수정 요청을 반영한 최종 문서만 Markdown으로 다시 작성하세요.
""",
        ),
    ]
    )

    guide_docs = retriever.invoke(question)
    guide = "\n\n".join(doc.page_content for doc in guide_docs)
    chain = revise_prompt | llm
    result = chain.invoke(
        {
            "guide": guide,
            "draft": current_doc,
            "question": question,
        }
    )

    return result.content

def create_doc(doc):
    st.markdown(doc)


if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="공문서 제작 도우미")
    st.title('공문서 제작 도우미')

    user_req = st.text_input(
        "만들고 싶은 문서는?",
        placeholder="예: 예산 변경 보고서, 기안서, 공고문",
    )

    if st.button('초안 생성'):
        if user_req:
            st.session_state.doc = draft_doc(user_req)
            st.session_state.state = "draft"
        else:
            st.error("요청을 넣어주세요.")

    if st.session_state.doc:
        if st.session_state.state == "completed":
            st.subheader("최종 문서")
            create_doc(st.session_state.doc)
            st.success("문서를 최종 확정했습니다.")
        else:
            revise_req = st.text_area(
                "수정하고 싶은 부분?",
                placeholder="예: 추진 배경을 더 짧게 하고, 일정 표를 추가해주세요.",
                height=100,
            )

            if st.button("수정 반영"):
                if revise_req:
                    st.session_state.doc = revise_doc(st.session_state.doc, revise_req)
                    st.session_state.state = "revised"
                    st.rerun()
                else:
                    st.error("수정 요청을 넣어주세요.")

            if st.button("이 문서로 확정"):
                st.session_state.state = "completed"
                st.rerun()

            st.divider()

            st.subheader("문서 미리보기")
            create_doc(st.session_state.doc)
            st.caption(f"현재 상태: {st.session_state.state}")
