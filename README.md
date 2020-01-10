### Requirements

Graphviz is used for charts generation. On MacOS you can install it with Homebrew:

```brew install graphviz```


### Install
Run `pipenv sync` in the root directory


### Usage

The following environment variables are required:
- `JIRA_HOST`, e.g. `https://your-domain.atlassian.net`
- `JIRA_USERNAME`, e.g. `your-email@example.com`
- `JIRA_TOKEN`, see how to set up token [here](https://confluence.atlassian.com/cloud/api-tokens-938839638.html) 

For example:
```
JIRA_HOST=domain JIRA_USERNAME=username JIRA_TOKEN=token pipenv run python jira_client.py --sprints "Sprint 80" "Sprint 81" --show_graph
```
