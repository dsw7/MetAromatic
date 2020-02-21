from sys import version_info

def is_valid_python_version(minimum):
    return bool(
        '.'.join([str(i) for i in version_info[0:2]]) >= minimum
    )
