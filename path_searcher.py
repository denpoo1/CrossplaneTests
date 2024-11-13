import os


def get_project_root_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current_dir, '..', ))


def get_config_path():
    project_root = get_project_root_path()
    return os.path.join(project_root, 'resourses', 'config.yaml')


def get_manifest_path():
    project_root = get_project_root_path()
    return os.path.join(project_root, 'manifests')

def get_manifest_path():
    project_root = get_project_root_path()
    return os.path.join(project_root, 'manifests')
