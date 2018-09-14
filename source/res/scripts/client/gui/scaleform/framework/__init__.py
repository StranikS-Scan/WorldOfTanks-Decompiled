# Embedded file name: scripts/client/gui/Scaleform/framework/__init__.py
from collections import namedtuple
from gui.Scaleform.framework import ViewTypes
import gui.Scaleform.framework.ViewTypes
import gui.Scaleform.framework.ScopeTemplates
from gui.Scaleform.framework.factories import EntitiesFactories, DAAPIModuleFactory, ViewFactory

class COMMON_VIEW_ALIAS(object):
    LOGIN = 'login'
    INTRO_VIDEO = 'introVideo'
    LOBBY = 'lobby'
    BATTLE = 'battle'
    CURSOR = 'cursor'
    WAITING = 'waiting'


ViewSettings = namedtuple('ViewSettings', ('alias', 'clazz', 'url', 'type', 'event', 'scope', 'cacheable'))
ViewSettings.__new__.__defaults__ = (None,
 None,
 None,
 None,
 None,
 None,
 False)
GroupedViewSettings = namedtuple('GroupedViewSettings', ('alias', 'clazz', 'url', 'type', 'group', 'event', 'scope', 'cacheable'))
GroupedViewSettings.__new__.__defaults__ = (None,
 None,
 None,
 None,
 None,
 None,
 None,
 False)
g_entitiesFactories = EntitiesFactories((DAAPIModuleFactory((ViewTypes.COMPONENT,)), ViewFactory((ViewTypes.DEFAULT,
  ViewTypes.LOBBY_SUB,
  ViewTypes.CURSOR,
  ViewTypes.WAITING,
  ViewTypes.WINDOW,
  ViewTypes.BROWSER,
  ViewTypes.TOP_WINDOW,
  ViewTypes.SERVICE_LAYOUT))))
