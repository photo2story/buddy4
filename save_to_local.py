# save_to_local.py

import os
from datetime import datetime

# 로컬 파일 경로 설정
LOG_FILE_PATH = 'search_history.log'

def get_current_content():
    if not os.path.exists(LOG_FILE_PATH):
        return ""
    
    with open(LOG_FILE_PATH, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def update_file(content):
    with open(LOG_FILE_PATH, 'w', encoding='utf-8') as file:
        file.write(content)
    print("File updated successfully.")

if __name__ == "__main__":
    # 현재 파일 내용 읽기
    current_content = get_current_content()
    print(f"Current {LOG_FILE_PATH} content:\n{current_content}")

    # 새로운 검색 기록 추가
    new_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: TEST\n"
    updated_content = current_content + new_entry

    # 파일 업데이트
    update_file(updated_content)

# python save_to_local.py