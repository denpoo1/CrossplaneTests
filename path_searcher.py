import os


def get_project_root_path():
    return os.path.dirname(os.path.abspath(__file__))


def get_config_path():
    project_root = get_project_root_path()
    return os.path.join(project_root, 'config.yaml')


def get_manifest_path():
    project_root = get_project_root_path()
    return os.path.join(project_root, 'manifests')
