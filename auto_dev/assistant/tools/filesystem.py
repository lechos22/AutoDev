import os
from langchain.tools import tool
import ast

from auto_dev import ANALYZED_PROJECT_PATH


@tool
def list_path(path: str) -> str:
    """
    Useful for listing a directory in the project, for example when looking for a file.
    When used for the first time, it's the best to use an empty string as the path.
    """
    try:
        path = os.path.realpath(os.path.join(ANALYZED_PROJECT_PATH, path))
        if not path.startswith(ANALYZED_PROJECT_PATH):
            raise RuntimeError("Unauthorized")
        if not os.path.isdir(path):
            raise RuntimeError("Not a directory")
        files = os.listdir(path)
        files = [
            file + int(os.path.isdir(os.path.join(path, file))) * "/" for file in files]
        return repr(files)
    except Exception as e:
        return repr(e)


@tool
def file_part(path: str) -> str:
    """Useful for reading a maximum of first 10 lines of a file."""
    try:
        path = os.path.realpath(os.path.join(ANALYZED_PROJECT_PATH, path))
        if not path.startswith(ANALYZED_PROJECT_PATH):
            raise RuntimeError("Unauthorized")
        if not os.path.isfile(path):
            raise RuntimeError("Not a text file")
        with open(path) as file:
            return repr(file.readlines()[:10])
    except Exception as e:
        return repr(e)


@tool
def file_summary(path: str) -> str:
    """Useful for getting top-level definitions present in a python file."""
    try:
        path = os.path.realpath(os.path.join(ANALYZED_PROJECT_PATH, path))
        if not path.startswith(ANALYZED_PROJECT_PATH):
            raise RuntimeError("Unauthorized")
        if not os.path.isfile(path):
            raise RuntimeError("Not a text file")
        with open(path) as file:
            text = file.read()
        tree = ast.parse(text)
        return repr({
            "classes": [node.name for node in ast.iter_child_nodes(tree) if isinstance(node, ast.ClassDef)],
            "functions": [node.name for node in ast.iter_child_nodes(tree) if isinstance(node, ast.FunctionDef)],
        })
    except Exception as error:
        return repr(error)


@tool
def read_class(path: str) -> str:
    """Useful for reading a class from given path in format <path>#<ClassName>."""
    try:
        path, class_name = path.split("#")
        path = os.path.realpath(os.path.join(ANALYZED_PROJECT_PATH, path))
        if not path.startswith(ANALYZED_PROJECT_PATH):
            raise RuntimeError("Unauthorized")
        if not os.path.isfile(path):
            raise RuntimeError("Not a text file")
        with open(path) as file:
            text = file.read()
        tree = ast.parse(text)
        return repr([ast.unparse(node) for node in ast.iter_child_nodes(tree) if isinstance(node, ast.ClassDef) and node.name == class_name])
    except Exception as e:
        return repr(e)
