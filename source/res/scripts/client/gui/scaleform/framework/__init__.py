# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/__init__.py
from collections import namedtuple
from gui.Scaleform.framework import ViewTypes
import gui.Scaleform.framework.ScopeTemplates
from gui.Scaleform.framework.factories import EntitiesFactories, DAAPIModuleFactory, ViewFactory

class COMMON_VIEW_ALIAS(object):
    """
    Common aliases of view.
    """
    LOGIN = 'login'
    INTRO_VIDEO = 'introVideo'
    LOBBY = 'lobby'
    BATTLE = 'battle'
    CURSOR = 'cursor'
    WAITING = 'waiting'


class GroupedViewSettings(namedtuple('GroupedViewSettings', 'alias clazz url type group event scope cacheable containers canDrag canClose isModal isCentered')):
    """
    Grouped view setting.
    
    :param alias: alias of view
    :param clazz: class of view
    :param url: url to SWF-file
    :param group: name of group
    :param type: type of view
    :param event: name of event for loading view
    :param cacheable: can be cached
    :param containers: list of sub containers
    :param canDrag: is drag & drop enabled
    :param canClose: is the view can be closed
    :param isModal: is the view is modal
    :param isCentered: is the view is centered on screen
    """

    def getDAAPIObject(self):
        return {'alias': self.alias,
         'url': self.url,
         'type': self.type,
         'event': self.event,
         'group': self.group,
         'isGrouped': self.group is not None,
         'canDrag': self.canDrag,
         'canClose': self.canClose,
         'isModal': self.isModal,
         'isCentered': self.isCentered}

    def replaceSettings(self, settings):
        return self._replace(**settings)


GroupedViewSettings.__new__.__defaults__ = (None,
 None,
 None,
 None,
 None,
 None,
 None,
 False,
 None,
 True,
 True,
 False,
 True)

class ViewSettings(GroupedViewSettings):
    """
    View setting.
    """

    @staticmethod
    def __new__(cls, alias, clazz, url, type, event, scope, cacheable, containers, canDrag, canClose, isModal, isCentered):
        """ overloaded ctor only for empty group passing reason """
        return GroupedViewSettings.__new__(cls, alias, clazz, url, type, None, event, scope, cacheable, containers, canDrag, canClose, isModal, isCentered)


ViewSettings.__new__.__defaults__ = (None,
 None,
 None,
 None,
 None,
 None,
 False,
 None,
 True,
 True,
 False,
 True)

class ContainerSettings(namedtuple('ContainerSettings', 'type clazz')):
    """
    Grouped view setting.
    
    :param type: type of container
    :param clazz: class of container
    """
    pass


ContainerSettings.__new__.__defaults__ = (None, None)
g_entitiesFactories = EntitiesFactories((DAAPIModuleFactory((ViewTypes.COMPONENT,)), ViewFactory((ViewTypes.DEFAULT,
  ViewTypes.LOBBY_SUB,
  ViewTypes.LOBBY_TOP_SUB,
  ViewTypes.CURSOR,
  ViewTypes.WAITING,
  ViewTypes.WINDOW,
  ViewTypes.BROWSER,
  ViewTypes.TOP_WINDOW,
  ViewTypes.OVERLAY,
  ViewTypes.SERVICE_LAYOUT))))
