from issue_graph import IssueGraph

graph = IssueGraph()
graph.add_issue('NET-11001', 'Task 1', '3')
graph.add_issue('NET-11002', 'Task 2', '5', labels=['Frontend'])
graph.add_issue('NET-11003', 'Task 3', '8', labels=['Backend'])

graph.add_link('NET-11001', 'NET-11002')
graph.add_link('NET-11001', 'NET-11003')
graph.add_link('NET-11002', 'NET-11003')

graph.show()
