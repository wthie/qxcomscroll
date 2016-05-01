#! /usr/bin/env python
#-*- coding: iso-8859-1 -*-

"""
qxplayground.py - the Qooxdoo playground

author     : Werner Thie, wth
last edit  : wth, 21.03.2011
modhistory :
  11.03.2010 - wth, created
"""

import sys, os, time

from twisted.internet import reactor
from twisted.python import log

from nevow import static, athena, loaders, inevow, url, tags as T, inevow, guard

from nevow.page import Element

from qxcomscroll.common.helpers   import uc, fourOfour

class QxPlayground(athena.LiveElement):
  jsClass = u'qxcomscroll.qxathena.qxplayground.QxPlayground'
    
  docFactory = loaders.xmlstr("""
    <div name='qxplayground' xmlns:nevow='http://nevow.com/ns/nevow/0.1' nevow:render='liveElement'>
    </div>
  """)
  
  def detached(self):
    #clean up whatever needs cleaning...
    log.msg('QxPlayground Object was detached cleanly')

  def connectionMade(self):
    print "Connected!"
    self.page.register(self)

  def connectionLost(self, reason):
    print "Disconnected!"

  @athena.expose
  def resetAll(self):
    self.page.resetAll()

  @athena.expose
  def toggleBeat(self):
    self.page.toggleBeat()

  def sendBeat(self, id, msg):
    """
    this is  the callback function doing the actual work
    """
    d = self.callRemote('beat', id, uc(msg))
     
  def reset(self):
    """
    this is  the callback function doing the actual work
    """
    d = self.callRemote('reset')

  @athena.expose
  def fourOfour(self, param):
    f = fourOfour()
    f.setFragmentParent(self)
    return f

  @athena.expose
  def getRsrcFile(self, fname):
    svg = ''
    name = os.path.abspath(fname)
    with open(name, 'rb') as f:
      svg = f.read()
    return uc(svg)
