import streamlit as st
from engine.processor import ContextFormatter

def render_ui():
    st.set_page_config(page_title="Context Loader MVP 🚀", layout="wide")
    st.header("🚀 Context Loader MVP")
    
    if "cleaned_context" not in st.session_state:
        st.session_state.cleaned_context = ""

    # 업로드 가능한 확장자에 pdf, docx 추가
    uploaded_file = st.file_uploader(
        "분석할 파일을 업로드하세요 (TXT, MD, PPTX, PDF, DOCX)", 
        type=['txt', 'md', 'pptx', 'pdf', 'docx']
    )
    
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        # 버튼을 누르면 엔진을 가동하도록 설정
        if st.button("데이터 정제 시작", type="primary"):
            with st.spinner("파일을 분석하고 문맥을 정제하는 중입니다..."):
                raw_bytes = uploaded_file.read()
                
                # 확장자별 분기 처리 (Branching)
                if file_extension == 'pptx':
                    st.session_state.cleaned_context = ContextFormatter.extract_from_pptx(raw_bytes)
                elif file_extension == 'pdf':
                    st.session_state.cleaned_context = ContextFormatter.extract_from_pdf(raw_bytes)
                elif file_extension == 'docx':
                    st.session_state.cleaned_context = ContextFormatter.extract_from_docx(raw_bytes)
                else:
                    # TXT, MD 파일 처리
                    raw_text = raw_bytes.decode("utf-8")
                    st.session_state.cleaned_context = ContextFormatter.clean_text(raw_text)
                    
                st.success("✅ 문맥 정제 완료!")

    # 정제된 결과가 있을 때만 결과창과 버튼 표시
    if st.session_state.cleaned_context:
        st.subheader("✅ 정제된 문맥 (Context)")
        
        # 대략적인 토큰 수 계산 (글자수 / 2.5 로 어림잡음)
        estimated_tokens = len(st.session_state.cleaned_context) // 2.5
        st.caption(f"Estimated Tokens(예상 토큰 수): 약 {int(estimated_tokens):,} 토큰")
        
        # 결과 텍스트 영역
        st.text_area("결과 복사하기", st.session_state.cleaned_context, height=400)
        
        # 다운로드 버튼 기능 (Export)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 .txt 파일로 다운로드",
                data=st.session_state.cleaned_context,
                file_name="cleaned_context.txt",
                mime="text/plain"
            )
        with col2:
            st.download_button(
                label="📥 .md 파일로 다운로드",
                data=st.session_state.cleaned_context,
                file_name="cleaned_context.md",
                mime="text/markdown"
            )