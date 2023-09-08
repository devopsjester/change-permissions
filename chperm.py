import os
import json
import logging
import requests
import getpass
import argparse


def get_access_token():
    # get the access token from an environment variable
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        logging.info("Found access token in environment variable")
        return token

    # get the access token from a file
    with open("access_token.txt", "r") as f:
        token = f.read().strip()
    if token:
        logging.info("Found access token in file")
        return token

    # get the access token from user input
    token = getpass.getpass(prompt="Enter your GitHub access token: ")
    if token:
        logging.info("Found access token from user input")
        return token

    # if no access token was found, exit the program
    logging.error("No access token found")
    print("No access token found")
    exit(1)

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

def change_repo_users_permissions(get_github_user_repos, get_repo_users, change_user_permission, owner, token, owner_type, excluded_users, original_permission, desired_permission):
    repos = get_github_user_repos(owner, owner_type, token)
    for repo in repos:
        change_users = get_repo_users(owner, repo, token, original_permission, excluded_users)
        logging.info(f"The users with {original_permission} rights for {owner}/{repo} are: {', '.join(change_users)}")
        print(f"The users with {original_permission} rights for {owner}/{repo} are: {', '.join(change_users)}")

        for user in change_users:
            change_user_permission(owner, repo, user, original_permission, desired_permission, token)


def change_org_users_permissions(owner, owner_type, excluded_users, original_permission, desired_permission, token):
    if owner_type != "orgs":
        logging.error(f"{owner} is not an organization")
        return

    # get the list of members of the organization
    members_url = f"https://api.github.com/orgs/{owner}/members"
    data = requests.get(members_url, headers={"Authorization": f"token {token}"})
    data.raise_for_status()
    members = data.json()
    logging.info(f"Found {len(members)} members for {owner}")

    # Change the permissions for each member
    for member in members:
        if member.get("login") in excluded_users:
            continue
        if member.get("site_admin") and original_permission == "member":
            continue
        if not member.get("site_admin") and original_permission == "admin":
            continue
        member_login = member.get("login")
        member_url = f"https://api.github.com/orgs/{owner}/memberships/{member_login}"
        member_data = {"role": desired_permission}
        member_response = requests.put(member_url, headers={"Authorization": f"token {token}"}, json=member_data)
        member_response.raise_for_status()
        logging.info(f"Changed {member_login}'s permission from {original_permission} to {desired_permission} in {owner}")
        print(f"Changed {member_login}'s permission from {original_permission} to {desired_permission} in {owner}")

def create_config_file():
    if not os.path.exists("chperm.config.json"):
        config = {
            "owner": "your_github_username_or_organization_name",
            "excluded_users": ["user1", "user2"],
            "original_org_permission": "admin",
            "desired_org_permission": "member",
            "original_repo_permission": "admin",
            "desired_repo_permission": "push"
        }
        with open("chperm.config.json", "w") as f:
            json.dump(config, f, indent=4)

if __name__ == "__main__":
    with open("chperm.config.json", "r") as f:
        config = json.load(f)

    logging.basicConfig(filename="chperm.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    
    owner = config["owner"]
    token = get_access_token()
    owner_type = get_owner_type(owner, token)
    excluded_users = config["excluded_users"]

    logging.info(f"Starting chperm.py for {owner}")    

    # get resource type (--org or --repos) from command line, or initialize the config file
    parser = argparse.ArgumentParser()
    parser.add_argument("--org", help="Change permissions for all repos in an organization", action="store_true")
    parser.add_argument("--repos", help="Change permissions for a list of repos", action="store_true")
    parser.add_argument("--init", help="Create a config file", action="store_true")
    args = parser.parse_args()
    
    if args.init:
        create_config_file()
        exit(0)

    if args.repos and not args.org:
        original_permission = config["original_repo_permission"]
        desired_permission = config["desired_repo_permission"]
        change_repo_users_permissions(get_github_user_repos, get_repo_users, change_user_permission, owner, token, owner_type, excluded_users, original_permission, desired_permission)
    elif args.org and not args.repos:
        original_permission = config["original_org_permission"]
        desired_permission = config["desired_org_permission"]
        change_org_users_permissions(owner, owner_type, excluded_users, original_permission, desired_permission, token)
    else:
        logging.error("Please specify either --org or --repos")
        print("Please specify either --org or --repos")