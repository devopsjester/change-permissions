# change-permissions

Takes the name of an `owner` (organization or user), iterates through all of the repositories, finds all of the users in each repository, and if they have a specified `source permission`, change it to the `target permission`.

## Instructions

In order to use this script, you must first set up a personal access token that has access to the owner of the repos (organization or user). Set up a *fine-grained* token (now available in public beta), it should be set with the following permissions:
- Organization permissions: **READ** access to members, **READ/WRITE** access to organization administration
- Repository permissions: **READ** access to metadata, **READ/WRITE** access to administration and code (content)

If you do not have access to *fine grained* tokens, e.g. you are running on GitHub Enterprise Server (GHES) *before* version 3.10, you will have to use a **GitHub App** to authenticate.

Configure the script by editing `chperm.config.json`. You may put the token in the config file (not recommended) or paste it in at the prompt after running the script.

To run the script, run `python chperm.py` from the command line. 
