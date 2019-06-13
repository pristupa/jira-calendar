import os
import tempfile
from typing import List

from graphviz import Digraph


class IssueGraph:
    issue_labels_html = {
        'Frontend': '<b><font color="#78c48c">Front</font></b>',
        'Backend': '<b><font color="#6268a3">Back</font></b>',
        'backend': '<b><font color="#6268a3">Back</font></b>',
    }

    def __init__(self):
        self.graph = Digraph(comment='Dependency graph')
        self.graph.node_attr.update(shape='box')
        self.graph.graph_attr.update(rankdir='LR')

    def add_issue(self, id_: str, summary: str, points: str, status: str, labels: List[str] = ()):
        short_summary = summary[:50] if summary else ''
        first_line = f'<b>{id_}</b>'
        for label in labels:
            first_line += ' ' + self.issue_labels_html.get(label, label)
        node_label = f'{first_line}<br/>{short_summary}'
        if points:
            node_label += f'<br/>Story points: {int(points)}'
        else:
            node_label += f'<br/><b><font color="#ff0000">No estimation</font></b>'
        self.graph.node(name=id_, label=f'<{node_label}>')

    def add_link(self, blocker: str, blocked: str):
        self.graph.edge(blocker, blocked)

    def show(self):
        directory = tempfile.gettempdir()
        filename = os.path.join(directory, 'dependency_graph.gv')
        self.graph.render(filename, view=True)
