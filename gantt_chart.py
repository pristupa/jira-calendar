import datetime
import os
import tempfile
from collections import defaultdict
from typing import List

from toposort import toposort_flatten

import gantt


class GanttChart:
    COLORS = {
        (): '#000000',
        ('FRONTEND',): '#78c48c',
        ('BACKEND',): '#6268a3',
        ('BACKEND', 'FRONTEND'): '#ff0000',
    }

    def __init__(self):
        self._tasks = {}
        self._dependencies = defaultdict(set)
        self._project = gantt.Project(name='Project 1')
        self._resources = {
            'egorov': gantt.Resource('egorov'),
            'pristupa': gantt.Resource('pristupa'),
        }

    def add_task(self, id_: str, title: str, points: int, labels: List[str] = ()):
        self._tasks[id_] = (title, points, tuple(sorted(label.upper() for label in labels)))
        len(self._dependencies[id_])  # For initializing defaultdict

    def add_dependency(self, blocker: str, blocked: str):
        self._dependencies[blocked].add(blocker)

    def show(self):
        today = datetime.datetime.now().date()
        result = toposort_flatten(self._dependencies)
        gantt_tasks = {}

        for id_ in result:
            gantt_tasks[id_] = task = gantt.Task(
                name=self._tasks[id_][0],
                start=today,
                duration=self._tasks[id_][1],
                depends_of=[gantt_tasks[blocker] for blocker in self._dependencies[id_]],
                #color=self.COLORS.get(self._tasks[id_][2], self.COLORS[()]),
                resources=list(self._resources.values()),
            )
            self._project.add_task(task)

        directory = tempfile.gettempdir()
        filename = os.path.join(directory, 'gantt_chart.svg')
        print(filename)
        self._project.make_svg_for_resources(filename=filename, today=today, resources=list(self._resources.values()))
