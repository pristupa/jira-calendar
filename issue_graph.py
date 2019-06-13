import os
import tempfile
from typing import List

from graphviz import Digraph


class IssueGraph:
    issue_labels_html = {
        'Frontend': '<font color="#78c48c">Front</font>',
        'Backend': '<font color="#6268a3">Back</font>',
    }

    def __init__(self):
        self.graph = Digraph(comment='Dependency graph')
        self.graph.node_attr.update(shape='box')

    def add_issue(self, id_: str, title: str, points: str, labels: List[str] = ()):
        short_title = title[:10]
        first_line = f'<b>{id_}</b>'
        for label in labels:
            first_line += ' ' + self.issue_labels_html.get(label, label)
        node_label = f'{first_line}<br/>{short_title}<br/>{points} points'
        self.graph.node(name=id_, label=f'<{node_label}>')

    def add_link(self, blocker: str, blocked: str):
        self.graph.edge(blocker, blocked)

    def show(self):
        directory = tempfile.gettempdir()
        filename = os.path.join(directory, 'dependency_graph.gv')
        self.graph.render(filename, view=True)
