import imp

import os
import os.path
import sys
import urlparse
import urllib2

import traceback

class URLLoader(object):
    stack = []

    def __init__(self, info):
        self.module_info = info
        return


    def load_module(self, name):
        print "LOAD_MODULE : NAME = %s" % (name)

        try:
            code_string = self.module_info["file"].read()

            module = sys.modules.setdefault(name, imp.new_module(name))
            module.__file__ = self.module_info["url"]
            module.__name__ = name
            module.__package__ = name

            if self.module_info["type"] == "package":
                module.__path__ = [self.module_info["url"]]
            elif self.module_info["type"] == "relative_package":
                module.__path__ = [self.module_info["url"]]
                module.__name__ = self.module_info["relative_package"]
                module.__package__ = ".".join(self.module_info["relative_package"].split(".")[:-1])
            elif self.module_info["type"] == "module":
                module.__path__ = self.module_info["url"]
                module.__package__ = ".".join(self.module_info["name"].split(".")[:-1])

            module.__loader__ = self

            URLLoader.stack.append(self.module_info["url"])
            code = compile(code_string, self.module_info["url"], "exec")
            exec code in module.__dict__
            sys.modules[name] = module
            URLLoader.stack.pop()

            return module

        except Exception, ex:
            print traceback.format_exc()
            print "Exception URLLoader.load_module %s" % ex
            raise ImportError, "Failed to import %s" % name

        return None

class URLLoaderEnv(object):
    known_path = []
    def __init__(self, path_entry):
        if path_entry.startswith("http://") or path_entry.startswith("https://"):
            print 'Checking URLLoader for %s' % path_entry
        else:
            raise ImportError()
        return

    def save_path(self, path, fullname):
        save_url = urlparse.urljoin(path, fullname.replace(".", "/"))
        for p in URLLoaderEnv.known_path:
            if p[1] == save_url:
                break
        else:
            URLLoaderEnv.known_path.insert(0, (fullname, save_url))


    def find_module(self, name, path = None):
        print "FIND_MODULE : NAME = %s PATH = %s" % (name, path)

        if path is None:
            path = sys.path

        for d in path:
            module_info = {"name": name}

            if d.startswith("http://") or d.startswith("https://"):
                save_path = urlparse.urljoin(d, name.replace(".", "/"))

                file_path = name.replace(".", "/") + ".py"
                url = urlparse.urljoin(d, file_path)
                try:
                    file = urllib2.urlopen(url)
                    self.save_path(d, name)

                    module_info["url"] = url
                    module_info["file"] = file
                    module_info["type"] = "module"

                    return URLLoader(module_info)
                except Exception, ex:
                    pass

                file_path = name.replace(".", "/") + "/__init__.py"
                url = urlparse.urljoin(d, file_path)
                try:
                    file = urllib2.urlopen(url)
                    self.save_path(d, name)

                    module_info["url"] = url
                    module_info["file"] = file
                    module_info["type"] = "package"

                    return URLLoader(module_info)
                except Exception, ex:
                    pass

                if len(URLLoader.stack) > 0:
                    file_path = name.replace(".", "/") + ".py"
                    url = urlparse.urljoin(URLLoader.stack[-1], file_path)
                    try:
                        file = urllib2.urlopen(url)
                        self.save_path(d, name)

                        module_info["url"] = url
                        module_info["file"] = file
                        module_info["type"] = "module"

                        return URLLoader(module_info)
                    except Exception, ex:
                        pass
                else:
                    for i in URLLoaderEnv.known_path:
                        file_path = name.replace(".", "/") + ".py"
                        url = urlparse.urljoin(i[1], file_path)
                        try:
                            file = urllib2.urlopen(url)

                            module_info["url"] = url
                            module_info["file"] = file
                            module_info["type"] = "relative_package"
                            module_info["relative_package"] = i[0]

                            return URLLoader(module_info)
                        except Exception, ex:
                            pass
        return None
