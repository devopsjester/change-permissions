import argparse
import requests
import logging

logging.basicConfig(filename='chperm.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

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
    parser = argparse.ArgumentParser(description='Get the admins for all repos of a GitHub owner')
    parser.add_argument('owner', type=str, help='the GitHub owner')
    parser.add_argument('token', type=str, help='the personal access token for GitHub API authentication')
    args = parser.parse_args()

    token = args.token
    owner = args.owner
    owner_type = get_owner_type(owner, token)

    repos = get_github_user_repos(owner, owner_type, token)
    for repo in repos:
        admins = get_repo_admins(owner, repo, token)
        logging.info(f"The admins for {owner}/{repo} are: {', '.join(admins)}")
        print(f"The admins for {owner}/{repo} are: {', '.join(admins)}")