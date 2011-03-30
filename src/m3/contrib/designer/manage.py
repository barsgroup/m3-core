#coding:utf-8
#!/usr/bin/env python

# Добавляем путь до django
import sys
import os
PATH_VENDOR = os.path.dirname( os.path.abspath(os.path.pardir) )

# Путь до vendor внутри m3
sys.path.insert(0, os.path.join(PATH_VENDOR, 'vendor') )

# Путь до m3
sys.path.insert(0, os.path.join(os.path.dirname(PATH_VENDOR)))

from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
