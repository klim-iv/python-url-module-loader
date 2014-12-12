import sys
import url_module_load

sys.path_hooks.append(url_module_load.URLLoaderEnv)
sys.path.append("http://svn.python.org/view/*checkout*/python/trunk/Lib/sqlite3/test/")
sys.path.append("https://raw.githubusercontent.com/klim-iv/python-url-module-loader/master/")

import dbapi
import example1.example2

dbapi.test()

