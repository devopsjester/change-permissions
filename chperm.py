import json
import logging
import requests
import getpass

def get_access_token():
    token = getpass.getpass(prompt="Enter your access token: ")
    return token

def get_owner_type(owner, token):
    url = f"https://api.github.com/users/{owner}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    if response.status_code == 200:
        type = data.get("type")
        if type == "Organization":
            logging.info(f"Found owner type: {type}")
            return "orgs"
        elif type == "User":
            logging.info(f"Found owner type: {type}")
            return "users"
        else:
            logging.error(f"Unknown owner type: {type}")
    else:
        logging.error(f"Error: {response.status_code}")

def get_github_user_repos(owner, owner_type, token):
    url = f"https://api.github.com/{owner_type}/{owner}/repos"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        logging.info(f"Found {len(data)} repos for {owner}")
        repos = []
        for repo in data:
            repos.append(repo.get("name"))
            logging.info(f"Found repo: {repo.get('name')}")
        return repos
    else:
        logging.error(f"Error: {response.status_code}")


def get_repo_admins(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/collaborators"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        logging.info(f"Found {len(data)} users for {owner}/{repo}")
        admins = []
        for user in data:
            if user.get("permissions").get("admin"):
                admins.append(user.get("login"))
                logging.info(f"Found admin: {user.get('login')}")
        return admins
    else:
        logging.error(f"Error: {response.status_code}")

if __name__ == "__main__":
    with open("chperm.config.json", "r") as f:
        config = json.load(f)

    owner = config["owner"]
    token = config["token"]
    if not token:
        token = get_access_token()
    owner_type = get_owner_type(owner, token)

    repos = get_github_user_repos(owner, owner_type, token)
    for repo in repos:
        admins = get_repo_admins(owner, repo, token)
        logging.info(f"The admins for {owner}/{repo} are: {', '.join(admins)}")
        print(f"The admins for {owner}/{repo} are: {', '.join(admins)}")