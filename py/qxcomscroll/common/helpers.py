#! /usr/bin/env python
#-*- coding: iso-8859-1 -*-

"""
helper funcs and classes

author   : Werner Thie, wth
last edit: wth, 20.01.2011
modhistory:
  20.01.2011 - wth, pruned for minimal
"""

import os, sys 

from nevow import static, athena, loaders, url, tags as T

def uc(msg):
  if type(msg) == type(''):
    return unicode(msg, 'iso-8859-1')
  else:
    return msg

def dc(msg):
  if type(msg) == type(''):
    return msg
  else:
    return msg.encode('iso-8859-1')

class fourOfour(athena.LiveElement):
  jsClass = u'common.helpers.fourOfour'
  
  docFactory = loaders.xmlstr("""
    <div xmlns:nevow="http://nevow.com/ns/nevow/0.1" nevow:render="liveElement">
    </div>
  """)
  

