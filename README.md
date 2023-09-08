# change-permissions
## (chprem)

`chperm` is a command-line tool that allows you to change the permissions of members in a GitHub organization or a list of repositories. You can use it to set the role of members from `admin` or `member` in an organization, or set it as `admin`, `triage`, `maintain`, `pull`, or `push` in a repository.

## Usage

### Initialize config file
Before using `chperm`, you need to create a config file by running:
```
python chperm.py --init
```

This will create a `chperm.config.json` file in the current directory with the following default values:
```
{
    "owner": "your_github_username_or_organization_name",
    "excluded_users": ["user1", "user2"],
    "original_org_permission": "admin",
    "desired_org_permission": "member",
    "original_repo_permission": "admin",
    "desired_repo_permission": "push"
}
```

You can modify these values to suit your needs.

### Change permissions for an organization
To change the permissions of members in a GitHub organization, run:

```
python chprem --org
```

### Change permissions for an organization's repos
To change the permissions of members in a GitHub organization's repos, run:

```
python chprem --repos
```

## Authentication

`chperm` uses a personal access token to authenticate with the GitHub API. You can create a personal access token by following the instructions [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

Once you have a personal access token, you must set it as an environment variable called `GITHUB_TOKEN`. Set up a *fine-grained* token (now available in public beta), it should be set with the following permissions:
- Organization permissions: **READ/WRITE** access to members, **READ/WRITE** access to organization administration
- Repository permissions: **READ** access to metadata, **READ/WRITE** access to administration and code (content)

If you do not have access to *fine grained* tokens, e.g. you are running on GitHub Enterprise Server (GHES) *before* version 3.10, you will have to use a **GitHub App** to authenticate.

