from langchain.graphs import Neo4jGraph

from auto_dev import config


class GraphDBProxy:
    def __init__(self):
        self.__graph = Neo4jGraph(**config['neo4j']['connection'])
        self.__project_id = config['dev-assistant']['context']['project-node-id']

    def receive_description_from_project_node(self):
        return self.__graph.query('''
MATCH (p:DjangoProject {id: $project_id}) RETURN p.description
''', {
            'project_id': self.__project_id
        })[0]['p.description']

    def receive_description_from_django_node(self):
        return self.__graph.query('''
MATCH (d:DjangoDescription) RETURN d.description
''')[0]['d.description']
