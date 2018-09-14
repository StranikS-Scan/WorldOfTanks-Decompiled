# Python bytecode 2.7 (decompiled from Python 2.7)
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


class GroupedViewSettings(namedtuple('GroupedViewSettings', 'alias clazz url type group event scope cacheable')):
    """
    :param alias: alias of view
    :param clazz: class of view
    :param url: url to SWF-file
    :param group: name of group
    :param type: type of view
    :param event: name of event for loading view
    :param cacheable: can be cached
    """

    def getDAAPIObject(self):
        return {'alias': self.alias,
         'url': self.url,
         'type': self.type,
         'event': self.event,
         'group': self.group,
         'isGrouped': self.group is not None}


GroupedViewSettings.__new__.__defaults__ = (None,
 None,
 None,
 None,
 None,
 None,
 None,
 False)

class ViewSettings(GroupedViewSettings):

    @staticmethod
    def __new__(cls, alias, clazz, url, type, event, scope, cacheable):
        """ overloaded ctor only for empty group passing reason """
        return GroupedViewSettings.__new__(cls, alias, clazz, url, type, None, event, scope, cacheable)


ViewSettings.__new__.__defaults__ = (None,
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
