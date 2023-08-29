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


def get_repo_users(owner, repo, token, original_permission, excluded_admins):
    url = f"https://api.github.com/repos/{owner}/{repo}/collaborators"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        logging.info(f"Found {len(data)} users for {owner}/{repo}")
        admins = []
        for user in data:
            if user.get("permissions").get("admin") and user.get("login") not in excluded_admins:
                admins.append(user.get("login"))
                logging.info(f"Found admin: {user.get('login')}")
        return admins
    else:
        logging.error(f"Error: {response.status_code}")

def change_user_permission(owner, repo, username, original_permission, desired_permission, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/collaborators/{username}"
    headers = {"Authorization": f"token {token}"}
    data = {"permission": desired_permission}
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 204:
        logging.info(f"Changed {username}'s permission from {original_permission} to {desired_permission} in {owner}/{repo}")
        print(f"Changed {username}'s permission from {original_permission} to {desired_permission} in {owner}/{repo}")
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
    excluded_users = config["excluded_users"]
    original_permission = config["original_permission"]
    desired_permission = config["desired_permission"]


    repos = get_github_user_repos(owner, owner_type, token)
    for repo in repos:
        change_users = get_repo_users(owner, repo, token, original_permission, excluded_users)
        logging.info(f"The users with {original_permission} rights for {owner}/{repo} are: {', '.join(change_users)}")
        print(f"The users with {original_permission} rights for {owner}/{repo} are: {', '.join(change_users)}")

        for user in change_users:
            change_user_permission(owner, repo, user, original_permission, desired_permission, token)