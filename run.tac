# run.tac - controlling file for a single instance webapp
# -*- coding: iso-8859-1 -*-

"""
This file is usually started with twistd -noy run.tac thus logging to the console.

 author   : Werner Thie, wth
 last edit: wth, 22.03.2011
 modhistory:
  20.01.2011 - wth, pruned for qxcomscroll
"""

import sys, os, shutil

from twisted.enterprise import adbapi

from twisted.cred import portal, credentials, checkers

from twisted.application import service, strports, internet

from twisted.internet import protocol, reactor

from twisted.conch import manhole, manhole_ssh

from twisted.python import log, util
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import LogFile

from nevow import appserver, athena

tbStripped = [
  './nevow',              #delete this, we're using our own code in this situation to fish for JS
  './pack',
  './qxcomscroll/js.src',
  './README'
]

def stripDistribution():
  print
  for f in tbStripped:
    path = os.path.abspath(f)
    if os.path.exists(path):
      if os.path.isdir(path):
        shutil.rmtree(path)
        print 'removed dir: ', path
      else:
        os.remove(path)
        print 'removed    : ', path
  print

if sys.platform.find('freebsd') == 0:
  stripDistribution()

tacpath, file  = os.path.split(__file__)
print 'this is                     : ', __file__
print 'on path                     : ', tacpath

sys.path.append(os.path.join(tacpath, 'py'))

mainPkgName = 'qxcomscroll'
import qxcomscroll
qxcomscroll.mainPkgName = mainPkgName
print '...using main module in py  : ', qxcomscroll.mainPkgName
athena.allJavascriptPackages()        #maps the basic runtime packages

#hunt down the related js files. Please note that the js.src is preferred over
#js, meaning that when in production the js.src could be killed and obfuscated
#and compressed js will be delivered out of packaged js directory
modulepath = os.path.join(os.path.split(qxcomscroll.__file__)[0], '..')

qxcomscroll.js = 'js'

#the JS source is preferred over the packaged version
if os.path.isdir(util.sibpath(modulepath, 'js.src')):
  qxcomscroll.js = 'js.src'
  
qxcomscroll.jspath = util.sibpath(modulepath, qxcomscroll.js)
qxcomscroll.siteJSPackage = athena.AutoJSPackage(qxcomscroll.jspath)
print '...using JS packages on path: ', qxcomscroll.jspath
print

#mechanism to switch between source and build target, reactivated and gaining complete debugging
#caps, but are at some more distance to our release target, which usually has its own problems
#when working in the source variant. Please switch to build for lightweight application code
#debugging and releasing/deploying code.
#For the implementation see code in mainpage.py fiddling with
#  self.jsClass = u'stirnrad.web.' + self.variant + u'.mainpage.Mainpage'
#and the accompanying two directories in js/web called build and source
#variant     = 'source'        #this is for deep debugging tasks also being able to dive into qooxdoo source
variant     = 'build'         #this is for app code debugging w/o being able to dive into qooxdoo source

print
print '****'
print '**** ', variant, 'variant running'
print '****'
if variant == 'source':
  print '**** !!!! please switch variant to build when releasing/deploying code !!!!'
  print '****'

qxathena = 'qxathena'

#resources are relative to the js for easy integration with JS frameworks
staticpath = os.path.join(qxcomscroll.jspath, mainPkgName, qxathena, variant, 'resource')
qooxdoopath = os.path.join(qxcomscroll.jspath, qxathena)

#special dictionary allowing you to relocate all image URI's of either the base library 'qx'
#or the qooxdoo application 'qxathena' to whatever path you desire giving the option to store
#images on webservers better suited to delivery of image content. If the dict is left empty 
#no image rebasing is done. The basic values when serving images with twisted are in this case.
#relocateImgs = {
#  u'qx': u'resource',
#  u'qxathena': u'resource'
#}
#After a quite panicky phase with servers under load at the end of week lead to a reinvestigation
#of the sanity of the approach and it was found healthy but not all to well described. Bear with
#me when diving into the innards of how qooxdoo finds images and stitches together the URIs for
#actually fetching them from the server. At the center of the qooxdoo mechanism lies a a structure
#in qx/util/ResourceManager.js, which is aptly named qx.$$libraries[lib].resourceUri. It's a 
#dictionary with keys named like the directories of the resources they're found under. The initial
#qooxdoo setup for this dict is as given above. If we want to rebase the images and fetch them from
#someplace else we simply exchange the URI in the dict under the given package (or directory) key,
#meaning that when the key qxathena is resolved by the resource manager to http://www.google.ch/resource
#the image requested with 'qxathena/images/ansagetafel.png' gets a final URI of the issued GET which
#looks like 'http://www.google.ch/resource/qxathena/images/ansagetafel.png'. Please don't forget to 
#use (u'') unicode encoded keys and strings, because only unicoded strings can be sent over the wire
relocateImgs = {
  u'qx': u'resource',
  u'qxathena': u'resource'
}

import qxcomscroll.web
qxcomscroll.gRSRC = qxcomscroll.web.TheRoot(staticpath, qooxdoopath, variant, relocateImgs)

#use this code below if you want to squeeze out whatever resources you have at hand. Remember
#psyco only works on 32bit platforms and has no meaning whatsoever on the new 64bit platforms
#It should be noted that system performance is almost alike with psyco on 32bit when compared to
#a non psyco version on 64bit. BTW, Python itself is usually compiled 32bit only, watch out for
#the Mac OSX 64bit standard python

if sys.platform != 'win32':
#  import psyco
#  psyco.full()
  UID = 80        													#set this to whatever uid/gid your system uses as webserver
  GID = 80        													#webserver uid/gid (80/80 is for FreeBSD)
  os.environ['PYTHON_EGG_CACHE'] = '/tmp'   #being downgraded means no access anymore so move
                                            #PYTHON_EGG_CACHE over someplace accessible

application = service.Application(mainPkgName)

#use this code below to configure logging in all aspects; keep in mind that for the log rotating code the
#access rights must be set such that the process has write access  to the log directory. A trick to adapt to
#get a logfile with the demoted process's UID/GID is to have an already existing file with all the properties
#set. LogFile will from then on create rotated files with the same properties .

#application.setComponent(ILogObserver, FileLogObserver(LogFile('jass.log', 'b:/', rotateLength=10000)).emit)

site = appserver.NevowSite(qxcomscroll.gRSRC)
webserver = strports.service("tcp:7999", site)
webserver.setServiceParent(application)

#def ManholeFactory(namespace, **passwords):
#  realm = manhole_ssh.TerminalRealm()
#
#  def getManhole(_):
#    return manhole.Manhole(namespace)
#
#  realm.chainedProtocolFactory.protocolFactory = getManhole
#  p = portal.Portal(realm)
#  p.registerChecker(checkers.InMemoryUsernamePasswordDatabaseDontUse(**passwords))
#  f = manhole_ssh.ConchFactory(p)
#  return f

#console = ManholeFactory(globals(), admin='admin')
#internet.TCPServer(2222, console, interface='localhost').setServiceParent(application)
