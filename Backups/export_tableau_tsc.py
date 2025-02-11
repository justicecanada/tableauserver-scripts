import os
from typing import Dict, List
import tableauserverclient as TSC
import argparse
import re

def _sanitize(name: str) -> str:
    """Sanitize a string by removing invalid characters with underscores"""
    invalid_chars_pattern = r'[<>:"/\\|?*;]'
    return re.sub(invalid_chars_pattern, '_', name)

def _truncate_name(name: str) -> str:
    #replace everythinng after the first occurence of '/' and trim
    return name.split('/')[0].strip()

def initialize_tableau_server(username: str, password: str, server: str = 'tableau', site: str = None):
    tableau_auth = TSC.TableauAuth(username, password, site)
    server = TSC.Server(f'https://{server}.justice.gc.ca')
    server.version = '3.14'
    server.use_server_version()
    server.add_http_options({'verify': False})
    print(f"Connected to Tableau server {server.server_address} with username {username} and site {site}")
    return server, tableau_auth


def get_all_datasources(server: TSC.Server, auth):
    # WIP: Get all datasources from Tableau server
    with server.auth.sign_in(auth):
        all_datasources, pagination_item = server.datasources.get()
        print("\nThere are {} datasources on site: ".format(pagination_item.total_available))
        print([datasource.name for datasource in all_datasources])


def save_workbook_to_file(server:TSC.Server, workbook_id: str, filepath: str | None = None):
    if filepath is None:
        filepath = f"{workbook_id}.twbx"
    server.workbooks.download(workbook_id, filepath=filepath)

class ProjectNode:
    def __init__(self, project: TSC.ProjectItem):
        self.project = project
        self.children = []
        self.level = 0

        self.project.name = _sanitize(_truncate_name(self.project.name))

    def __str__(self):
        return f"{self.project.name} ({self.project.id})"
    
def _print_project_tree(nodes: ProjectNode, level=0):
    ### Print project tree. Useful for debugging    
    for node in nodes:
        print("  " * level + f"- {node.project.name} (ID: {node.project.id})")
        _print_project_tree(node.children, level + 1)

def get_projects_hierarchy(server: TSC.Server) -> List[ProjectNode]:    
    # Build project hierarchy
    projects = {project.id: ProjectNode(project) for project in TSC.Pager(server.projects)}
    
    # Build tree structure
    root_nodes = []
    for project_id, node in projects.items():
        if node.project.parent_id is None:
            root_nodes.append(node)
        else:
            parent = projects.get(node.project.parent_id)
            if parent:
                parent.children.append(node)
                node.level = parent.level + 1
    
    return root_nodes
        

def get_all_workbooks(server: TSC.Server, auth, base_path: str = 'workbooks'):
    with server.auth.sign_in(auth):
        project_hierarchy = get_projects_hierarchy(server)        

        # Get and download workbooks while preserving project hierarchy
        for workbook in TSC.Pager(server.workbooks):
            # retrieve the project with the workbook's project ID from the project hierarchy, check recursively.
            def find_project(projects: List[ProjectNode], project_id: str, path: str = base_path):
                for project in projects:
                    current_path = f"{project.project.name}" if not path else f"{path}/{project.project.name}"
                    if project.project.id == project_id:
                        return project, current_path
                    result, child_path = find_project(project.children, project_id, current_path)
                    if result:
                        return result, child_path
                return None, ""
            
            project, path = find_project(project_hierarchy, workbook.project_id)            
            os.makedirs(path, exist_ok=True)
            
            try:
                save_workbook_to_file(server, workbook.id, os.path.join(path, _sanitize(workbook.name)))
            except Exception as e:
                print(f"Error saving workbook {workbook.name}: {e}")    


def main():
    #parse arguments
    parser = argparse.ArgumentParser(description='Export workbooks and datasources from Tableau server')    
    parser.add_argument('username', type=str, help='Tableau server username')
    parser.add_argument('password', type=str, help='Tableau server password')
    parser.add_argument('server', type=str, help='Tableau server address (default: tableau)')
    parser.add_argument('--site', '-s', type=str, help='Tableau server site (default: None)')
    parser.add_argument('--log-level', '-l', choices=['debug', 'info', 'error'], default='error', help='Set desired logging level (default: error)')

    args = parser.parse_args()

    try:
        server, tableau_auth = initialize_tableau_server(args.username, args.password, args.server, args.site)
        # get_all_datasources(server, tableau_auth)
        get_all_workbooks(server, tableau_auth)
        #get_projects_hierarchy(server, tableau_auth)
    except Exception as e:
        print(f"Error connecting to Tableau server: {e}")
    finally:
        if 'server' in locals() and hasattr(server, 'auth'):
            server.auth.sign_out()

if __name__ == '__main__':
    main()
    

