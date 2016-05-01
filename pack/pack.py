#!/usr/bin/env python
#
# notes:
# custom_rhino.jar from:
#   http://dojotoolkit.org/svn/dojo/buildscripts/lib/custom_rhino.jar
#
# author   : Bob Ippolito and friends
#            adapted for our purposes by Werner Thie, wth
# last edit: wth, 15.07.2010
# modhistory:
#   11.11.2008 - wth, refined version for tutorials
#   13.07.2010 - wth, adapted to the qooxdoo project structure
#   15.07.2010 - wth, packs everything with .js extension and > 2048 Bytes 

"""
This script when run in its directory looks for the files collected in FILES relative
to where it was started from, processes and packs them and stores the packed versions
of those files in the same hierarchy as the source versions with the js.src directory
for the packed versions shortened to js. This allows for easy killing the source dir 
when distributing the server.

    /pack/pack.py
    |
    /main/js.src/xxx.js
                      /yyy.js
                      /anotherdir/
                                 anotherfile.js
"""

import os
import re
import sys
import shutil
import subprocess
import gzip

if sys.platform == 'win32':
  JSLint = 'jsl.exe'
elif sys.platform == 'darwin':
  JSLint = 'jsl'
  
jspackagepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../js.src'))
hasJSLint = os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), JSLint)))
                           
FILES = []

#list files here which are already packed and should not be processed any further but 
#simply copied over to the new directory tree
ALREADYPACKED = [
  'qxathena.js',
]

#lists simple patterns which suppress the copying of files altogether
IGNORE = [
  os.path.sep + 'source', 
  os.path.sep + 'index.html',
  '.json',
  '.py',
  '.svn',
  'json2.js'  
]

GZIPTYPES = [
  '.js',
]

JSLINTEXCLUDES = [
]

#copied this snippet over from athena and adapted it slightly for my needs.
#Just skipped the regexp deoctoring for yielding the full line with the match in it
#and restored the import later on. May be a mightier sould than I will do it
_importExpression = re.compile('^// import (.+)$', re.MULTILINE)

def extractImports(fileObj):
  res = []
  s = fileObj.read()
  for m in _importExpression.finditer(s):
    res.append(m.group(1).decode('ascii'))
  return res

for root, dirs, fnames in os.walk(jspackagepath):
  for fname in fnames:
    fn = os.path.join(root, fname)
    ignore = False
    for pattern in IGNORE:
      ignore |= fn.find(pattern) != -1
    if not ignore: 
      FILES.append(fn)

for fname in FILES:
  newfname = fname.replace('.src', '')
  if not os.path.isdir(os.path.dirname(newfname)):
    os.makedirs(os.path.dirname(newfname))
  if os.path.basename(fname) in ALREADYPACKED or os.path.splitext(fname)[1] != '.js':
    if os.path.basename(fname) in ALREADYPACKED:  #ugly, but we don't need the other info
      print
      print '>>>>>>> ', os.path.basename(fname)
      print '-------    copying file: ', os.path.abspath(fname)
    shutil.copy(fname, newfname)
  else:
    if os.path.split(fname)[1] not in JSLINTEXCLUDES and hasJSLint:
      print
      print '>>>>>>> ', os.path.basename(fname)
      print '-------    linting file: ', os.path.abspath(fname)
      p = subprocess.Popen(
        ['jsl', '-process', os.path.abspath(fname), '-conf', 'jsl.conf', '-nologo'],
        stdout=subprocess.PIPE)
      linted = p.stdout.read()
      print linted
    print '-------    packing file: ', os.path.abspath(fname)
    outf = file(newfname, 'w')
    p = subprocess.Popen(
      ['java', '-jar', 'custom_rhino.jar', '-c', os.path.abspath(fname)],
      stdout=subprocess.PIPE)
    packed = p.stdout.read()
    orgf = file(fname, 'r')
    imports = extractImports(orgf)
    orgf.close()
    for i in imports:
      outf.write('// import %s\n' % i)
    outf.write(packed)
    outf.close()
  
  if os.path.splitext(fname)[1] in GZIPTYPES:
    msg = '------- NOT zipped file:  ' + os.path.abspath(fname)   
    inf = file(newfname, 'rb')
    packed = inf.read()
    inf.close()
    if len(packed) > 2048:
      zipf = gzip.open(newfname + '.gz', 'wb', 6)
      zipf.write(packed)
      zipf.close()
      msg = '-------     zipped file:  ' + os.path.abspath(fname)  
    print msg


