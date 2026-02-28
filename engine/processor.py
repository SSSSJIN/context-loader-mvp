import re
import io
from pptx import Presentation
import PyPDF2
import docx

class ContextFormatter:
    """텍스트 데이터의 가독성을 높이고 AI의 인식률을 개선하는 모듈입니다."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'(?<=[가-힣a-zA-Z0-9])\n(?=[가-힣a-zA-Z0-9])', ' ', text)
        text = re.sub(r'[^\w\s\.\?\!\,\(\)\|\[\]\-가-힣]', '', text) # 마크다운 기호(|, -, [, ]) 허용
        return text.strip()

    @staticmethod
    def _parse_pptx_table(shape) -> str:
        """PPTX 내의 표를 Markdown(마크다운) 형식으로 변환합니다."""
        table_text = "\n"
        for row_idx, row in enumerate(shape.table.rows):
            row_data = [cell.text.replace('\n', ' ').strip() for cell in row.cells]
            table_text += "| " + " | ".join(row_data) + " |\n"
            # 첫 번째 행(Header) 아래에 구분선 추가
            if row_idx == 0:
                table_text += "|" + "|".join(["---"] * len(row.cells)) + "|\n"
        return table_text + "\n"

    @staticmethod
    def extract_from_pptx(file_bytes: bytes) -> str:
        """메타데이터(슬라이드 번호)와 표 마크다운 변환을 포함하여 텍스트를 추출합니다."""
        try:
            prs = Presentation(io.BytesIO(file_bytes))
            text_runs = []
            
            for i, slide in enumerate(prs.slides, 1):
                slide_text = []
                for shape in slide.shapes:
                    # 표(Table) 처리
                    if shape.has_table:
                        slide_text.append(ContextFormatter._parse_pptx_table(shape))
                    # 일반 텍스트 및 숨김 도형 제외 (has_text_frame 확인)
                    elif hasattr(shape, "text") and shape.has_text_frame:
                        text = shape.text.strip()
                        if text:
                            slide_text.append(text)
                
                if slide_text:
                    # Metadata Tagging(메타데이터 태깅, 출처 표시)
                    text_runs.append(f"\n\n[Slide {i}]\n" + "\n".join(slide_text))
                    
            return ContextFormatter.clean_text("".join(text_runs))
        except Exception as e:
            return f"PPTX 텍스트 추출 중 오류가 발생했습니다: {e}"

    @staticmethod
    def extract_from_docx(file_bytes: bytes) -> str:
        """DOCX에서 단락과 표(마크다운)를 순차적으로 추출합니다."""
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            text_runs = []
            
            # 단락 추출
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_runs.append(paragraph.text.strip())
                    
            # 표 추출 (문서 하단에 마크다운으로 추가)
            if doc.tables:
                text_runs.append("\n\n[문서 내 표 데이터]")
                for table in doc.tables:
                    for row_idx, row in enumerate(table.rows):
                        row_data = [cell.text.replace('\n', ' ').strip() for cell in row.cells]
                        text_runs.append("| " + " | ".join(row_data) + " |")
                        if row_idx == 0:
                            text_runs.append("|" + "|".join(["---"] * len(row.cells)) + "|")
                    text_runs.append("\n")

            return ContextFormatter.clean_text("\n".join(text_runs))
        except Exception as e:
            return f"DOCX 텍스트 추출 중 오류가 발생했습니다: {e}"

    @staticmethod
    def extract_from_pdf(file_bytes: bytes) -> str:
        """PDF에서 페이지 번호(메타데이터)와 함께 텍스트를 추출합니다."""
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text_runs = []
            for i, page in enumerate(reader.pages, 1):
                extracted_text = page.extract_text()
                if extracted_text:
                    text_runs.append(f"\n\n[Page {i}]\n" + extracted_text)
            return ContextFormatter.clean_text("".join(text_runs))
        except Exception as e:
            return f"PDF 텍스트 추출 중 오류가 발생했습니다: {e}"