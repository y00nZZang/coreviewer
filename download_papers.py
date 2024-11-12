import openreview
import requests
import os
import random
import shutil

# OpenReview 클라이언트 초기화
client = openreview.Client(baseurl='https://api.openreview.net')

# 특정 컨퍼런스의 논문 목록 가져오기 (예: ICLR 2023)
conference_id = 'ICLR.cc/2023/Conference'
notes = list(openreview.tools.iterget_notes(client, invitation=conference_id + '/-/Blind_Submission'))

# 논문 20개 랜덤 선택
random_papers = random.sample(notes, 20)

# PDF 다운로드 및 저장 디렉토리 설정
data_dir = './data'
os.makedirs(data_dir, exist_ok=True)

for note in random_papers:
    paper_id = note.id
    pdf_path = note.content.get('pdf', '')

    if pdf_path:
        # 스키마 추가
        pdf_url = f"https://openreview.net{pdf_path}"

        # PDF 다운로드
        response = requests.get(pdf_url, stream=True)

        if response.status_code == 200:
            pdf_file_path = f"{data_dir}/{paper_id}.pdf"

            with open(pdf_file_path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)

            print(f"PDF 다운로드 완료: {pdf_file_path}")
        else:
            print(f"Failed to download PDF for paper ID: {paper_id}")
    else:
        print(f"No PDF path found for paper ID: {paper_id}")