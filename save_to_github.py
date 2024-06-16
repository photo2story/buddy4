# save_to_github.py

import requests
import base64
import os
from datetime import datetime

# 환경 변수에서 GitHub 토큰 가져오기
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = 'photo2story'
REPO_NAME = 'buddy4'
FILE_PATH = 'search_history.log'
API_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github+json'
}

def get_file_sha():
    response = requests.get(API_URL, headers=HEADERS)
    if response.status_code == 200:
        file_info = response.json()
        return file_info['sha']
    return None

def get_current_content():
    response = requests.get(API_URL, headers=HEADERS)
    if response.status_code == 200:
        file_info = response.json()
        content = base64.b64decode(file_info['content']).decode('utf-8')
        return content
    return ""

def update_file(content, sha):
    data = {
        "message": "Update search history",
        "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
        "sha": sha
    }
    response = requests.put(API_URL, headers=HEADERS, json=data)
    if response.status_code == 200:
        print("File updated successfully.")
    else:
        print(f"Failed to update file: {response.json()}")

def create_file(content):
    data = {
        "message": "Create search history",
        "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')
    }
    response = requests.put(API_URL, headers=HEADERS, json=data)
    if response.status_code == 201:
        print("File created successfully.")
    else:
        print(f"Failed to create file: {response.json()}")

if __name__ == "__main__":
    current_content = get_current_content()
    print(f"Current {FILE_PATH} content:\n{current_content}")

    new_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: TEST\n"
    updated_content = current_content + new_entry

    file_sha = get_file_sha()
    if file_sha:
        update_file(updated_content, file_sha)
    else:
        print(f"File not found: {FILE_PATH}. Creating a new file.")
        create_file(updated_content)

# .\\.venv\\Scripts\\activate
# python save_to_github.py