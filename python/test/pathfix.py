def fix_sys_path():
    import sys
    import os
    from os import path
    join = path.join
    ufile = path.realpath(join(os.getcwd(), path.expanduser(__file__)))
    for p in ["..", join("..", "multiplay")]:
        sys.path.append(path.normpath(join(path.dirname(ufile), p)))