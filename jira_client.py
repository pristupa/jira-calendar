import os
import sys
from collections import defaultdict
from typing import List

from jira import Issue
from jira import JIRA

from gantt_chart import GanttChart
from issue_graph import IssueGraph

username = os.environ.get('JIRA_USERNAME')
token = os.environ.get('JIRA_TOKEN')

options = {'server': os.environ.get('JIRA_HOST')}
cookie = (username, token)
auth_jira = JIRA(options, basic_auth=cookie)

epic_keys = sys.argv[1:]
jql = ' OR '.join(f'"Epic Link"={epic_key}' for epic_key in epic_keys)
issues: List[Issue] = auth_jira.search_issues(jql, maxResults=False)


def is_closed(issue) -> bool:
    return issue.fields.status.name not in ('In Progress', 'Opened')


total_points = 0
total_points_per_label = defaultdict(int)
not_estimated_issues = []
issue_graph = IssueGraph()
gantt_chart = GanttChart()
for issue in issues:
    if is_closed(issue):
        continue
    story_points = issue.fields.customfield_10005
    status_name = issue.fields.status.name
    issue_graph.add_issue(
        issue.key,
        summary=issue.fields.summary,
        points=story_points,
        status=status_name,
        labels=issue.fields.labels,
    )
    gantt_chart.add_task(issue.key, issue.key, int(story_points or '0'), issue.fields.labels)
    for issue_link in issue.fields.issuelinks:
        if issue_link.type.name == 'Blocks' and hasattr(issue_link, 'outwardIssue'):
            if not is_closed(issue_link.outwardIssue):
                issue_graph.add_link(issue.key, issue_link.outwardIssue.key)
                gantt_chart.add_dependency(issue.key, issue_link.outwardIssue.key)

    if story_points:
        total_points += int(story_points)
        for label in issue.fields.labels:
            total_points_per_label[label] += int(story_points)
    else:
        not_estimated_issues.append(issue)

print(f'Total issues: {len(issues)}')
print(f'Not estimated issues: {len(not_estimated_issues)}')
print(f'Total points: {total_points}')
for label, points in total_points_per_label.items():
    print(f'{label} points: {points}')
issue_graph.show()
gantt_chart.show()
