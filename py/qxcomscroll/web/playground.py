#! /usr/bin/env python
#-*- coding: iso-8859-1 -*-

"""
playground - the basic object which serves as the root
             
author   : Werner Thie, wth
last edit: wth, 21.03.2011
modhistory:
  03.06.2009 - wth, thinking about disconnecting
  21.03.2011 - wth, reworked for qxcomscroll
"""

import os, sys, time, random

from zope.interface import implements

from twisted.python import util, log

from twisted.internet import defer

from nevow import static, athena, loaders, url, tags as T, inevow, guard
from nevow.page import renderer

from qxcomscroll.common.i18n    import _TStr, getTexts
from qxcomscroll.common.helpers import uc, dc

from qxcomscroll.qxathena.qxathena import QxAthena

REQ_404        = -1
REQ_ROOT       = 0
REQ_WITHID     = 2

class Playground(athena.LiveElement):
  jsClass = u'qxcomscroll.web.playground.Playground'
  
  docFactory = loaders.xmlstr("""
    <div xmlns:nevow="http://nevow.com/ns/nevow/0.1" nevow:render="liveElement"
      class="playground" name="playground" 
      style="width: 100%; height: 100%; min-height: 100%; position: absolute; left: 0px; top: 0px; background-color: #c2c2c2;">
      <img id="waitroller" src="waitroller.gif" style="width: 100px; height: 100px; top: 50%; left: 50%; position: absolute; margin-left: -50px; margin-top: -50px;"/>
    </div>
  """)
  
  PG_UNKNOWN   = -1
  PG_INITED    =  0
  
  def __init__(self, uid=None):
    super(Playground, self).__init__()
    self.state = self.PG_INITED
    self.uid = uid

  def detached(self):
    #clean up whatever needs cleaning...
    log.msg('playground object was detached cleanly')

  @athena.expose
  def inject_404(self):
    f = fourOfourMsg()
    f.setFragmentParent(self)
    return f

  @athena.expose
  def QxAthena(self, params):
    f = QxAthena()
    f.setFragmentParent(self)
    return f

  @athena.expose
  def getTexts(self, ids):
    return getTexts(map(dc, ids), self.page.lang)

  @athena.expose
  def guiready(self):    
    def usermatch(user):  #select usually returns a list, knowing that we have unique results
      reqtype = REQ_404   #the result is unpacked already and a single item returned
      udata = {}
      if len(user) > 0:
        self.page.userid   = user['id']
        reqtype = REQ_WITHID
        for k in user.keys():
          if type(user[k]) == type(''):
            udata[uc(k)] = uc(user[k])
          else:
            udata[uc(k)] = user[k] 
      return reqtype, udata

    def rootmatch(res):    #select usually returns a list, knowing that we have unique results
      reqtype = REQ_ROOT   #the result is unpacked already and a single item returned
      udata = {}
      user  = {}
      user['id'] = self.page.username
      for k in user.keys():
        if type(user[k]) == type(''):
          udata[uc(k)] = uc(user[k])
        else:
          udata[uc(k)] = user[k] 
      return reqtype, udata
    
    if self.uid and len(self.uid) == 32:
      d = self.page.userstore.getUserWithUID(self.uid)
      d.addCallback(usermatch)
      d.addErrback(nomatch)
    else:
      d = defer.succeed(0)
      d.addCallback(rootmatch)
      
    return d
