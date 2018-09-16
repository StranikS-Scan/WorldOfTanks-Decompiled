# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/__init__.py
from collections import namedtuple
from gui.Scaleform.framework import ViewTypes
import gui.Scaleform.framework.ScopeTemplates
from gui.Scaleform.framework.factories import EntitiesFactories, DAAPIModuleFactory, ViewFactory
from gui.Scaleform.framework.settings import UIFrameworkImpl

class COMMON_VIEW_ALIAS(object):
    LOGIN = 'login'
    INTRO_VIDEO = 'introVideo'
    LOBBY = 'lobby'
    BATTLE = 'battle'
    CURSOR = 'cursor'
    WAITING = 'waiting'


class GroupedViewSettings(namedtuple('GroupedViewSettings', 'alias clazz url type group event scope cacheable containers canDrag canClose isModal isCentered')):

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

    def toImmutableSettings(self):
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
 True)

class ViewSettings(GroupedViewSettings):

    @staticmethod
    def __new__(cls, alias, clazz, url, type, event, scope, cacheable, containers, canDrag, canClose, isModal, isCentered):
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
    pass


ContainerSettings.__new__.__defaults__ = (None, None)

class ConditionalViewSettings(GroupedViewSettings):

    @staticmethod
    def __new__(cls, alias, clazzFunc, url, type, group, event, scope, cacheable, containers, canDrag, canClose, isModal, isCentered):
        self = GroupedViewSettings.__new__(cls, alias, '', url, type, group, event, scope, cacheable, containers, canDrag, canClose, isModal, isCentered)
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
 True)
g_entitiesFactories = EntitiesFactories((DAAPIModuleFactory((ViewTypes.COMPONENT,)), ViewFactory((ViewTypes.MARKER,
  ViewTypes.DEFAULT,
  ViewTypes.LOBBY_SUB,
  ViewTypes.LOBBY_TOP_SUB,
  ViewTypes.CURSOR,
  ViewTypes.WAITING,
  ViewTypes.WINDOW,
  ViewTypes.BROWSER,
  ViewTypes.TOP_WINDOW,
  ViewTypes.OVERLAY,
  ViewTypes.SERVICE_LAYOUT))))
