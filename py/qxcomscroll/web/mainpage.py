#! /usr/bin/env python
#-*- coding: utf-8 -*-

"""
mainpage.py - this is the place where everything is happening, the user will never
              ever see a page change during the whole visit. Everything the user iw
              shown is injected as a LiveElement into the page and deleted after it
              has served its purpose.

              The main element which resides in this page and handles all aspects of
              user interaction is the playground. It has a first go at the arguments
              and then injects whatever is needed. 
              
              Due to the fact that webapps are highly user driven, the main interaction
              points are usually triggered from the client, whereas things such as status
              updates or realtime data delivery is handled by the server at its own pace
              
author   : Werner Thie, wth
last edit: wth, 07.02.2013
modhistory:
  20.01.2011 - wth, pruned for minimal demo app
  07.02.2013 - wth, introduced img preloading in the page template for mobile Safari
"""

import os, sys, time, random

try:
  import hashlib
  md5_constructor = hashlib.md5
except ImportError:
  import md5
  md5_constructor = md5.md5

try:
  from twisted.web import http
except ImportError:
  from twisted.protocols import http

from zope.interface import implements

from twisted.python import util, log

from twisted.internet import reactor

from nevow import static, athena, loaders, url, tags as T, inevow, guard
from nevow.page import renderer
from nevow.compression import parseAcceptEncoding
from nevow.inevow import IRequest
from nevow.useragent import UserAgent

import qxcomscroll
from qxcomscroll.common.i18n    import _TStr
from qxcomscroll.common.helpers import uc

from qxcomscroll.web.playground import Playground

COOKIEKEY = 'qxcomscroll'

class mainPageFactory:
  noisy = True

  def __init__(self):
    self.clients = {}
    """
    Was one hell of an expensive line, the basic underlying plugin mechanism does not work in
    vhost situation where everything sits in the same basic namespace, clashes are preprogrammed.
    I decided to fiddle with the package mappings and arrived at a clean version of my packages but,
    my mappings didn't connect with the mappings collected by other mechanisms. The final trick was
    to update the module global mapping in jsDeps with my collection, the lonly line below does the trick 
    """
    athena.jsDeps.mapping.update(qxcomscroll.siteJSPackage.mapping)

  def addClient(self, client):
    clientID = self._newClientID()
    self.clients[clientID] = client
#      if self.noisy:
#        log.msg("Rendered new mainPage %r: %r" % (client, clientID))
#        log.msg("Number of active pages currently: %d" % len(self.clients))
    return clientID

  def getClient(self, clientID):
    return self.clients[clientID]

  def removeClient(self, clientID):
    # State-tracking bugs may make it tempting to make the next line a
    # 'pop', but it really shouldn't be; if the Page instance with this
    # client ID is already gone, then it should be gone, which means that
    # this method can't be called with that argument.
    del self.clients[clientID]
#      if self.noisy:
#        log.msg("Disconnected old LivePage %r" % (clientID,))

  def _newClientID(self):
    return guard._sessionCookie()

_mainPageFactory = mainPageFactory()
_mainPageFactory.noisy = False
                
class MappingCompressedResource(athena.MappingResource):
  """
  L{inevow.IResource} which looks up segments in a mapping between symbolic
  names and the files they correspond to. Additionally if a compressed version
  is present and content negotiation allows zipped resources, the zipped
  file is preferred  

  @type mapping: C{dict}
  @ivar mapping: A map between symbolic, requestable names (eg,
  'Nevow.Athena') and C{str} instances which name files containing data
  which should be served in response.
  """
  implements(inevow.IResource)

  def __init__(self, mapping):
    self.mapping = mapping
      
  def canCompress(self, req):
    """
    Check whether the client has negotiated a content encoding we support.
    """
    value = req.getHeader('accept-encoding')
    if value is not None:
      encodings = parseAcceptEncoding(value)
      return encodings.get('gzip', 0.0) > 0.0
    return False


  def resourceFactory(self, fileName):
    """
    Retrieve a possibly  L{inevow.IResource} which will render the contents of
    C{fileName}.
    """
    f = open(fileName, 'rb')
    js = f.read()
    return static.Data(js, 'text/javascript')


  def locateChild(self, ctx, segments):
    try:
      impl = self.mapping[segments[0]]
    except KeyError:
      return rend.NotFound
    else:
      req = IRequest(ctx)
      implgz = impl + '.gz'
      if self.canCompress(req) and os.path.exists(implgz):
        impl = implgz
        req.setHeader('content-encoding', 'gzip')
      return self.resourceFactory(impl), []


class MainPage(athena.LivePage):
  relocateimgs = True
  addSlash = True
  factory = _mainPageFactory

  docFactory = loaders.htmlstr(u"""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xmlns:nevow="http://nevow.com/ns/nevow/0.1">
      <head>
        <title nevow:data="title" nevow:render="data">Page Title</title>
        <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
        <nevow:invisible nevow:render="liveglue" />
        <style type="text/css">
          html { 
            height: 100%; 
          }
          body { 
            min-height: 100%; 
          }          
          * html body {
            height: 100%;
          }
          .hide {
            display:none;
          }
        </style>
      </head>
      <body style="margin: 0px; padding: 0px; overflow: hidden; height: 100%; width: 100%;">
        <nevow:invisible nevow:render="playground" />
        <img class="hide" src="{relocate}/qxathena/images/error.png"/>
      </body>
    </html>
  """)

  def child_jsmodule(self, ctx):
    return MappingCompressedResource(self.jsModules.mapping)

  def data_title(self, ctx, data):
    return self.pageTitle

  #if you need a place where to keep things during the LifePage being up, please
  #do it here and only here. Storing states someplace deeper in the hierarchy makes
  #it extremely difficult to release memory properly due to circular object refs 
  def beforeRender(self, ctx):
    self.page.lang = 3
    self.uid = None
    self.username = ''
    self.pageTitle = _TStr('WelcomeTitle', self.page.lang)
    self.qooxdoopath = _QOOXDOOPATH
    self.variant = _VARIANT
    self.jsClass = u'qxcomscroll.web.' + self.variant + u'.mainpage.Mainpage'
    self.relocateImgs = _RELOCATEIMGS
    if self.relocateimgs:
      self.docFactory.template = self.docFactory.template.replace(u'{relocate}', self.relocateImgs['qxathena'])
      self.relocateimgs = False     
    d = self.notifyOnDisconnect()
    d.addErrback(self.disconn)
    self.playground = None
    
  def register(self, playground):
    self.playground = playground
    
  def toggleBeat(self):
    global running
    if running:
      running = False
    else:
      beatMachine()
  
  def resetAll(self):
    global beats
    beats = 0
    resetAll()
    
  def sendBeat(self, id, msg):
    """
    callback message directed to registered object, aka playground
    """
    if self.playground:
      self.playground.sendBeat(id, msg)
  
  def reset(self):
    """
    callback message directed to registered object, aka playground
    """
    if self.playground:
      self.playground.reset()
    
  def render_playground(self, ctx, data):
    f = Playground(self.uid)
    f.setFragmentParent(self)
    return ctx.tag[f]

  def disconn(self, reason):
    """
    we will be called back when the client disconnects, clean up whatever needs
    cleaning serverside
    """
    self.playground = None

mobileClients = {
}

def isMobileClient(request):      
  agentString = request.getHeader("user-agent")
  if agentString is None:
    return False
  agent = UserAgent.fromHeaderValue(agentString)
  if agent is None:
    return False

  requiredVersion = mobileClients.get(agent.browser, None)
  if requiredVersion is not None:
    return agent.version >= requiredVersion 
  return False

beats = 0
running = False

def beatMachine():
  global running, beats
  def doBeat():
    global beats
    for liveid in _mainPageFactory.clients.keys():
      msg = 'do something fancy...'
      _mainPageFactory.clients[liveid].sendBeat(beats, msg)
    beats += 1
    if running:
      reactor.callLater(1.0, doBeat)
  if not running:
    beats = 0
    running = True
    doBeat()

def resetAll():
  for liveid in _mainPageFactory.clients.keys():
    _mainPageFactory.clients[liveid].reset()
          
def factory(ctx, segments):
  """
  If segments contains a liveID the page stored in self.clients will be returned. Status 
  of the given page is stored in the page object itself and nowhere else.
  """
  seg0 = segments[0]
  if seg0 == '':
    if isMobileClient(inevow.IRequest(ctx)):
      return mobilePage(), segments[1:]
    else:
      return MainPage(), segments[1:]
  elif _mainPageFactory.clients.has_key(seg0):
    return _mainPageFactory.clients[seg0], segments[1:]
  elif len(seg0) == 32:
    IRequest(ctx).addCookie(COOKIEKEY, seg0, http.datetimeToString(time.time() + 30.0))
    return url.URL.fromString('/'), ()
  else:
    return None, segments