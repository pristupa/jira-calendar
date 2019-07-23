import os
import sys
from collections import defaultdict
from typing import List

from jira import Issue
from jira import JIRA
import argparse

from gantt_chart import GanttChart
from issue_graph import IssueGraph

username = os.environ.get('JIRA_USERNAME')
token = os.environ.get('JIRA_TOKEN')

options = {'server': os.environ.get('JIRA_HOST')}
cookie = (username, token)
auth_jira = JIRA(options, basic_auth=cookie)


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--epics', type=str, nargs='+')
parser.add_argument('--sprints', type=str, nargs='+')
args = parser.parse_args()

jql = ' OR '.join([
    ' OR '.join(f'"Epic Link"={epic_key}' for epic_key in args.epics),
    ' OR '.join(f'"Sprint"="{sprint_key}"' for sprint_key in args.sprints),
])
issues: List[Issue] = auth_jira.search_issues(jql, maxResults=False)


def is_closed(issue) -> bool:
    return issue.fields.status.name not in ('In Progress', 'Opened')


def is_bug(issue) -> bool:
    return issue.fields.issuetype.name in ('Defect', 'Bug')


def is_subtask(issue) -> bool:
    return issue.fields.issuetype.name in ('Sub-task', )


bugs = [issue for issue in issues if is_bug(issue) and not is_closed(issue)]
total_bugs = len([issue for issue in issues if is_bug(issue)])
issues = [issue for issue in issues if not is_subtask(issue) and not is_bug(issue)]
total_issues = len(issues)
total_points = 0
for issue in issues:
    story_points = issue.fields.customfield_10005
    if story_points:
        total_points += int(story_points)

issues = [issue for issue in issues if not is_closed(issue)]

remaining_points = 0
total_points_per_label = defaultdict(int)
not_estimated_issues = []
issue_graph = IssueGraph()
gantt_chart = GanttChart()
for issue in issues:
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
        remaining_points += int(story_points)
        for label in issue.fields.labels:
            total_points_per_label[label] += int(story_points)
    else:
        not_estimated_issues.append(issue)

bugs_per_label = defaultdict(list)
for bug in bugs:
    for label in bug.fields.labels:
        bugs_per_label[label].append(bug)
    if not bug.fields.labels:
        bugs_per_label['Not investigated'].append(bug)

print(f'Remaining issues: {len(issues)} (of {total_issues})')
print(f'Not estimated issues: {len(not_estimated_issues)}')

print()
print(f'Remaining points: {remaining_points} (of {total_points})')
for label, points in total_points_per_label.items():
    print(f'{label} points: {points}')

print()
print(f'Remaining bugs and defects: {len(bugs)} (of {total_bugs})')
for label, label_bugs in bugs_per_label.items():
    print(f'{label}: {len(label_bugs)}')

issue_graph.show()
gantt_chart.show()
