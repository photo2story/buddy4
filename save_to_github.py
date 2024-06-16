# save_to_github.py

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "photo2story"
REPO_NAME = "buddy4"
FILE_PATH = "search_history.log"
BRANCH = "main"

def get_file_sha(repo_owner, repo_name, file_path):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("sha")
    elif response.status_code == 404:
        return None
    else:
        print(f"Failed to get file SHA: {response.json()}")
        return None

def update_file(repo_owner, repo_name, file_path, content, sha, branch):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "message": f"Update {file_path}",
        "content": content.encode("utf-8").decode("utf-8"),
        "sha": sha,
        "branch": branch
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Successfully updated {file_path}")
    else:
        print(f"Failed to update {file_path}: {response.json()}")

def main():
    sha = get_file_sha(REPO_OWNER, REPO_NAME, FILE_PATH)
    if sha is None:
        print(f"File not found: {FILE_PATH}. Creating a new file.")
        content = ""
    else:
        url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{FILE_PATH}"
        response = requests.get(url)
        content = response.text

    print(f"Current {FILE_PATH} content:\n{content}")

    new_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: TEST\n"
    content += new_line
    encoded_content = content.encode("utf-8").decode("utf-8")

    update_file(REPO_OWNER, REPO_NAME, FILE_PATH, encoded_content, sha, BRANCH)

if __name__ == "__main__":
    main()

    save_search_history_to_github("LLY")

# .\\.venv\\Scripts\\activate
# python save_to_github.py