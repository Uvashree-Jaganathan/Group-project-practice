import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/malavika/turtle_py_ws/install/turtle_py_pkg'
