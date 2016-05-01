#! /usr/bin/env python
#-*- coding: iso-8859-1 -*-

"""
Site organisation things collected

author   : Werner Thie, wth
last edit: wth, 13.06.2011
modhistory:
  20.01.2011 - wth, pruned for minimal
  31.01.2011 - wth, created qxcomscroll as analogue
  13.06.2011 - wth, fiddling with the paths, bringing everything up to qooxdoo V1.4.1
"""

import os, sys, re, gc

from zope.interface import implements

from twisted.python import util, log

from twisted.internet import task

from nevow import inevow, static, rend, loaders, url, tags as T

import qxcomscroll.common.dumpobj

import qxcomscroll.web.mainpage

class FileNoListDir(static.File):
  def directoryListing(self):
    return error.ForbiddenResource()

class TheRoot(rend.Page):
  def __init__(self, staticpath, qooxdoopath, variant, relocateImgs, *args, **kw):
    super(TheRoot, self).__init__(*args, **kw)
    qxcomscroll.web.mainpage._STATICPATH  = staticpath
    qxcomscroll.web.mainpage._QOOXDOOPATH = qooxdoopath
    qxcomscroll.web.mainpage._VARIANT     = variant
    qxcomscroll.web.mainpage._RELOCATEIMGS= relocateImgs    
    self.children = {
      variant                     : FileNoListDir(os.path.join(qooxdoopath, variant)),
      os.path.split(staticpath)[1]: FileNoListDir(staticpath),
      'favicon.ico'               : FileNoListDir(os.path.join(staticpath, 'qxathena', 'images', 'favicon.ico')),
      'waitroller.gif'            : FileNoListDir(os.path.join(staticpath, 'qxathena', 'images', 'waitroller.gif'))
    }
    if variant == 'source':     #we need the SDK path included in case of running the source version
      if sys.platform == 'win32':
        self.children['qooxdoo'] = FileNoListDir('c:\\proj\\qooxdoo')
      else:
        #to solve the problem getting at the qx resources use a symbolic link to qx in the build directory
        #in the source/resource directory do
        # ln -s ../../build/resource/qx qx
        #the symbolic link created is ignored by SVN! But, be aware that when the build directory
        #is erased and a rebuild via the generator script is attempted this will fail, because the
        #link cannot be stat'd. Just create the build directory chain the link is pointing to with
        #mkdir -p build/resource/qx and the
        #python generate.py source
        #will run again with no flaws
        self.children['qooxdoo'] = FileNoListDir('/proj/qooxdoo')
        self.children['source']  = FileNoListDir(os.path.join(staticpath, '..'))             #theme files are requested via variant
      self.children['script']    = FileNoListDir(os.path.join(staticpath, '..', 'script'))
    print #separate package hinting from logging

  def locateChild(self, ctx, segments):
    rsrc, segs = qxcomscroll.web.mainpage.factory(ctx, segments)
    if rsrc == None:
      rsrc, segs = super(TheRoot, self).locateChild(ctx, segments)
    return rsrc, segs

exc = [
  "function",
  "type",
  "list",
  "dict",
  "tuple",
  "wrapper_descriptor",
  "module",
  "method_descriptor",
  "member_descriptor",
  "instancemethod",
  "builtin_function_or_method",
  "frame",
  "classmethod",
  "classmethod_descriptor",
  "_Environ",
  "MemoryError",
  "_Printer",
  "_Helper",
  "getset_descriptor",
  "weakreaf"
]

inc = [
]

prev = {}

def dumpObjects(delta=True, limit=0, include=inc, exclude=[]):
  global prev
  if include != [] and exclude != []:
    print 'cannot use include and exclude at the same time'
    return
  print 'working with:'
  print '   delta: ', delta
  print '   limit: ', limit
  print ' include: ', include
  print ' exclude: ', exclude
  objects = {}
  gc.collect()
  oo = gc.get_objects()
  for o in oo:
    if getattr(o, "__class__", None):
      name = o.__class__.__name__
      if ((exclude == [] and include == [])       or \
          (exclude != [] and name not in exclude) or \
          (include != [] and name in include)):
        objects[name] = objects.get(name, 0) + 1
##    if more:
##      print o
  pk = prev.keys()
  pk.sort()
  names = objects.keys()
  names.sort()
  for name in names:
    if limit == 0 or objects[name] > limit:
      if not prev.has_key(name):
        prev[name] = objects[name]
      dt = objects[name] - prev[name]
      if delta or dt != 0:
        print '%0.6d -- %0.6d -- ' % (dt, objects[name]),  name
      prev[name] = objects[name]

def getObjects(oname):
  """
  gets an object list with all the named objects out of the sea of
  gc'ed objects
  """
  olist = []
  objects = {}
  gc.collect()
  oo = gc.get_objects()
  for o in oo:
    if getattr(o, "__class__", None):
      name = o.__class__.__name__
      if (name == oname):
        olist.append(o)
  return olist

dumpObject = qxcomscroll.common.dumpobj


