import argparse
import os
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


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--epics', type=str, nargs='+', default=[])
parser.add_argument('--sprints', type=str, nargs='+', default=[])
parser.add_argument('--releases', type=str, nargs='+', default=[])
parser.add_argument('--show_gantt', action='store_true', default=False)
parser.add_argument('--show_graph', action='store_true', default=False)
args = parser.parse_args()

filters = []
if args.epics:
    filters.append(' OR '.join(f'"Epic Link"={epic_key}' for epic_key in args.epics))
if args.sprints:
    filters.append(' OR '.join(f'"Sprint"="{sprint_key}"' for sprint_key in args.sprints))
if args.releases:
    filters.append(' OR '.join(f'fixVersion="{release}"' for release in args.releases))

jql = ' OR '.join(filters)
issues: List[Issue] = auth_jira.search_issues(jql, maxResults=False)


def is_closed(issue) -> bool:
    return False
    return issue.fields.status.raw['id'] == '6'  # Closed


def is_bug(issue) -> bool:
    return issue.fields.issuetype.name in ('Defect', 'Bug')


def is_subtask(issue) -> bool:
    return issue.fields.issuetype.name.startswith('Sub')


bugs = [issue for issue in issues if is_bug(issue) and not is_closed(issue)]
total_bugs = len([issue for issue in issues if is_bug(issue)])
issues = [issue for issue in issues if not is_subtask(issue) and not is_bug(issue)]
total_issues = len(issues)
total_points = 0
issues = [issue for issue in issues if not is_closed(issue)]

remaining_points = 0
total_points_per_label = defaultdict(int)
not_estimated_issues = []
issue_graph = IssueGraph()
gantt_chart = GanttChart()
visited_keys = {issue.key for issue in issues}
while len(issues) > 0:
    issue = issues.pop()
    story_points = getattr(issue.fields, 'customfield_10005', None)
    if story_points:
        total_points += int(story_points)
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
        if issue_link.type.name == 'Blocks':
            if hasattr(issue_link, 'inwardIssue') and issue_link.inwardIssue.key not in visited_keys:
                inward_issue = auth_jira.issue(issue_link.inwardIssue.key)
                visited_keys.add(inward_issue.key)
                issues.append(inward_issue)
            if hasattr(issue_link, 'outwardIssue') and not is_closed(issue_link.outwardIssue):
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

issue_graph.save(view=args.show_graph)
if args.show_gantt:
    gantt_chart.show()
