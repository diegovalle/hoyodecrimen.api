#!/usr/bin/python
import os
 
virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
os.environ['PYTHON_EGG_CACHE'] = os.path.join(virtenv, 'lib/python2.7/site-packages')
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass
 
from hoyodecrimen import app as application