#! /usr/bin/env python
#-*- coding: iso-8859-1 -*-

"""
qxathena.py - a minimal Qooxdoo integration attempt

author     : Werner Thie, wth
last edit  : wth, 21.03.2011
modhistory :
  11.03.2010 - wth, created
  04.02.2011 - wth, signals production run back to client counterpart, thus 
                    reducing logging on the client
"""

import sys, os

from twisted.internet import reactor
from twisted.python import log

from nevow import static, athena, loaders, inevow, url, tags as T, inevow, guard

from nevow.page import Element

import qxcomscroll

from qxplayground import QxPlayground

class QxAthena(athena.LiveElement):
  jsClass = u'qxcomscroll.qxathena.qxathena.QxAthena'

  docFactory = loaders.xmlstr("""
    <div xmlns:nevow="http://nevow.com/ns/nevow/0.1" nevow:render="liveElement"
      name="QxAthena" class="QxAthena" 
      style="visibility: hidden; width: 100%; height: 100%; position: absolute; left: 0px; top: 0px;">
      <div id="qooxdoo-root"
        style="width: 100%; height: 100%; position: absolute; left: 0px; top: 0px;">
      </div>
    </div>
  """)
  
  @athena.expose
  def initQooxdoo(self, param):
    log.msg('---- initQooxdoo called')
    return qxcomscroll.js == 'js', self.page.relocateImgs

  @athena.expose
  def QxPlayground(self, param):
    f = QxPlayground()
    f.setFragmentParent(self)
    return f

  def detached(self):
    #clean up whatever needs cleaning...
    log.msg('QxAthena object was detached cleanly')
