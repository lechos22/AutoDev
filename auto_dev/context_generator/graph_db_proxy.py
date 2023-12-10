from langchain.graphs import Neo4jGraph

from auto_dev import config


class GraphDBProxy:
    def __init__(self):
        self.__graph = Neo4jGraph(**config['neo4j']['connection'])
        self.__project_id = config['dev-assistant']['context']['project-node-id']

    def check_if_project_node_exists(self):
        return self.__graph.query('''
MATCH (p:DjangoProject) RETURN
    CASE 
        WHEN COUNT(p) > 0 THEN true 
        ELSE false
    END AS result
''')[0]['result']

    def clear_old_nodes(self):
        self.__graph.query('''
DELETE ()
''')

    def create_django_description(self, django_description_md: str):
        return self.__graph.query('''
MERGE (p:DjangoDescription)
SET p.description = $django_description_md
''', {
            'django_description_md': django_description_md
        })

    def create_project_node(self, project_name: str, project_description: str):
        return self.__graph.query('''
MERGE (p:DjangoProject {id: $project_id})
SET p.name = $name
SET p.description = $description
''', {
            'project_id': self.__project_id,
            'name': project_name,
            'description': project_description
        })

    def create_django_description_node(self, django_description: str):
        return self.__graph.query('''
MERGE (dd:DjangoDescription)
SET dd.description = $description
''', {
            'description': django_description
        })

    def create_django_app_node(self, app_name: str):
        self.__graph.query('''
MATCH (p:DjangoProject {id: $project_id})
CREATE (:DjangoApp {name: $name})-[:COMPONENT_OF]->(p)
''', {
            'project_id': self.__project_id,
            'name': app_name
        })

    def create_file_node(self, file_path: str, file_content: str):
        self.__graph.query('''
CREATE (:ProjectFile {path: $path, content: $content})
''', {
            'path': file_path,
            'content': file_content
        })

    def create_python_code_fragment_node(
            self,
            file_path: str,
            fragment_id: int,
            code: str,
            description: str,
            start_line: int,
            end_line: int
    ):
        self.__graph.query('''
MATCH (f:ProjectFile  {path: $file_path})
CREATE (p:PythonCodeFragment {
    path: $file_path, fragment_id: $fragment_id, code: $code, start_line: $start_line, end_line: $end_line
})-[:DEFINED_IN]->(f)
''', {
            'file_path': file_path,
            'fragment_id': fragment_id,
            'code': code,
            'description': description,
            'start_line': start_line,
            'end_line': end_line
        })

    def connect_files_to_project(self, file_paths: list[str]):
        self.__graph.query('''
MATCH (p:DjangoProject {id: $project_id})
UNWIND $file_paths AS file_to_connect
MATCH (f: ProjectFile {path: file_to_connect})
CREATE (f)-[:BELONGS_TO]->(p)
''', {
            'project_id': self.__project_id,
            'file_paths': file_paths
        })

    def connect_files_to_django_app(self, file_paths: list[str], app_name: str):
        self.__graph.query('''
MATCH (p:DjangoProject {id: $project_id})<-[:COMPONENT_OF]-(a:DjangoApp {name: $app_name})
UNWIND $file_paths AS file_to_connect
MATCH (f: ProjectFile {path: file_to_connect})
CREATE (f)-[:BELONGS_TO]->(a)
''', {
            'project_id': self.__project_id,
            'app_name': app_name,
            'file_paths': file_paths
        })

