from pdfminer.high_level import extract_text
import os

# 입력 및 결과 디렉토리 설정
data_dir = './data'
result_dir = './results_extract_text'
os.makedirs(result_dir, exist_ok=True)

# PDFMiner로 텍스트 추출
def extract_text_with_pdfminer(pdf_path):
    return extract_text(pdf_path)

# 각 PDF 파일에 대해 텍스트 추출 및 저장
for pdf_file in os.listdir(data_dir):
    if pdf_file.endswith('.pdf'):
        pdf_path = os.path.join(data_dir, pdf_file)
        paper_id = os.path.splitext(pdf_file)[0]

        # 텍스트 추출
        text = extract_text_with_pdfminer(pdf_path)

        # 결과 저장
        text_file_path = os.path.join(result_dir, f"{paper_id}_pdfminer.txt")
        with open(text_file_path, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"PDFMiner 결과 저장 완료: {text_file_path}")