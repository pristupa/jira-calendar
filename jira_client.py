import os
import sys
from typing import List

from jira import Issue
from jira import JIRA
from issue_graph import IssueGraph

username = os.environ.get('JIRA_USERNAME')
token = os.environ.get('JIRA_TOKEN')

options = {'server': os.environ.get('JIRA_HOST')}
cookie = (username, token)
auth_jira = JIRA(options, basic_auth=cookie)

epic_keys = sys.argv[1:]
jql = ' OR '.join(f'"Epic Link"={epic_key}' for epic_key in epic_keys)
issues: List[Issue] = auth_jira.search_issues(jql, maxResults=False)

issue_graph = IssueGraph()
for issue in issues:
    issue_graph.add_issue(issue.key, issue.key, '1')
    for issue_link in issue.fields.issuelinks:
        if issue_link.type.name == 'Blocks' and hasattr(issue_link, 'outwardIssue'):
            issue_graph.add_link(issue.key, issue_link.outwardIssue.key)

issue_graph.show()
