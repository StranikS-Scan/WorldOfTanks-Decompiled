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


class GroupedViewSettings(namedtuple('GroupedViewSettings', 'alias clazz url type group event scope cacheable containers canDrag canClose isModal isCentered isResizable')):
    """
    Grouped view setting.
    
    :param alias: alias of view
    :param clazz: class of view
    :param url: url to SWF-file
    :param type: type of view
    :param group: name of group
    :param event: name of event for loading view
    :param scope: scope
    :param cacheable: can be cached
    :param containers: list of sub containers
    :param canDrag: is drag & drop enabled
    :param canClose: is the view can be closed
    :param isModal: is the view is modal
    :param isCentered: is the view is centered on screen
    :param isResizable: can the view be resized
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
         'isCentered': self.isCentered,
         'isResizable': self.isResizable}

    def replaceSettings(self, settings):
        return self._replace(**settings)

    def toImmutableSettings(self):
        """ Returns object equivalent to self, with all lazy data evaluations (if any) complete.
            Data in returned object must never change afterwards.
            Base GroupedViewSettings is already immutable, so this method returns self by default.
        
        :return: immutable settings object (self if already immutable, or a copy after lazy evaluations)
        """
        return self


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
 True,
 True)

class ViewSettings(GroupedViewSettings):
    """
    View setting.
    """

    @staticmethod
    def __new__(cls, alias, clazz, url, type, event, scope, cacheable, containers, canDrag, canClose, isModal, isCentered, isResizable):
        """ overloaded ctor only for empty group passing reason """
        return GroupedViewSettings.__new__(cls, alias, clazz, url, type, None, event, scope, cacheable, containers, canDrag, canClose, isModal, isCentered, isResizable)


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
 True,
 True)

class ContainerSettings(namedtuple('ContainerSettings', 'type clazz')):
    """
    Grouped view setting.
    
    :param type: type of container
    :param clazz: class of container
    """
    pass


ContainerSettings.__new__.__defaults__ = (None, None)

class ConditionalViewSettings(GroupedViewSettings):

    @staticmethod
    def __new__(cls, alias, clazzFunc, url, type, group, event, scope, cacheable, containers, canDrag, canClose, isModal, isCentered, isResizable):
        self = GroupedViewSettings.__new__(cls, alias, '', url, type, group, event, scope, cacheable, containers, canDrag, canClose, isModal, isCentered, isResizable)
        self.__clazzFunc = clazzFunc
        self.__url = url
        self.__type = type
        self.__scope = scope
        self.__group = group
        return self

    @property
    def clazz(self):
        return self.__clazzFunc()

    @property
    def url(self):
        return self.__url() if callable(self.__url) else self.__url

    @property
    def type(self):
        return self.__type() if callable(self.__type) else self.__type

    @property
    def scope(self):
        return self.__scope() if callable(self.__scope) else self.__scope

    @property
    def group(self):
        return self.__group() if callable(self.__group) else self.__group

    def toImmutableSettings(self):
        return GroupedViewSettings(*self._replace(clazz=self.clazz, url=self.url, type=self.type, scope=self.scope, group=self.group))


ConditionalViewSettings.__new__.__defaults__ = (None,
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
 True,
 True)
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
