#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
i18n.py - translation and resources file, depending on the language code
          0 - german
          1 - french
          2 - italian
          and the id passed in does deliver the requested textual resource

author   : Werner Thie, wth
last edit: wth, 20.01.2011
modhistory:
  20.01.2011 - wth, pruned for minimal
"""
import os

from helpers import uc, dc

pText = {
  'WelcomeTitle': (
    u'Willkommen bei qxcomscroll',
    u'fra Willkommen bei qxcomscroll',
    u'ita Willkommen bei qxcomscroll',
    u'Welcome to qxcomscroll'
  ),         
  'discoError': (
    u'<font size=3><b>Die Verbindung zum Server wurde unterbrochen</b></font><font size=2><br>Mögliche Ursachen können Server-Probleme, Unterbrechungen der Internet-Verbindung (bei Ihrem Provider) oder Ihre Internet-Anbindung selbst sein. Falls Sie mit einer Wireless-Verbindung surfen, stellen Sie sicher, dass Sie eine ausreichende und konstante Signalstärke haben.</font>',
    u'fra <font size=3><b>Die Verbindung zum Server wurde unterbrochen</b></font><font size=2><br>Mögliche Ursachen können Server-Probleme, Unterbrechungen der Internet-Verbindung (bei Ihrem Provider) oder Ihre Internet-Anbindung selbst sein. Falls Sie mit einer Wireless-Verbindung surfen, stellen Sie sicher, dass Sie eine ausreichende und konstante Signalstärke haben.</font>',
    u'ita <font size=3><b>Die Verbindung zum Server wurde unterbrochen</b></font><font size=2><br>Mögliche Ursachen können Server-Probleme, Unterbrechungen der Internet-Verbindung (bei Ihrem Provider) oder Ihre Internet-Anbindung selbst sein. Falls Sie mit einer Wireless-Verbindung surfen, stellen Sie sicher, dass Sie eine ausreichende und konstante Signalstärke haben.</font>',
    u'<font size=3><b>Connection to server interupted</b></font><font size=2><br>Reasons for such problems can be the server or interruptions of your Internet connection. In case of being connected to the Internet with WiFi please make sure that you have a decent signal</font>'
  ),         
  'textidentifier1': (
    u'ein anderer deutscher Text',
    u'fra ein anderer deutscher Text',
    u'ita ein anderer deutscher Text',
    u'just another german text'
  )
}

def _TStr(id, lang):
  try:
    text = pText[id][lang]
  except KeyError, IndexError:
    text = "Key: '%s' for language: %d not found" % (id, lang)
  return text

#given a list of id's return a dict with the strings  
def getTexts(ids, lang):
  td = {}
  for id in ids:
    td[uc(id)] = _TStr(id, lang)
  return td
