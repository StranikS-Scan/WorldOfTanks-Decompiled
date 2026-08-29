# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/event_banners/event_banners_container.py
from __future__ import absolute_import
import typing
import Event
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Dict, Type
    from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner

class EventBannersContainer(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EventBannersContainer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
        self.__eventsMap = {}
        self.onBannerUpdate = Event.Event()
        self._initialized = True

    @property
    def events(self):
        return self.__eventsMap

    def registerEventBanner(self, eventBannerCls):
        if self.__eventsMap.has_key(eventBannerCls.NAME):
            raise SoftException('Banner for key {0} is already registered'.format(eventBannerCls.NAME))
        self.__eventsMap[eventBannerCls.NAME] = eventBannerCls()

    def getEventBanner(self, key):
        return self.__eventsMap.get(key)

    def unregisterEventBanner(self, eventBannerCls):
        banner = self.__eventsMap.pop(eventBannerCls.NAME)
        if banner is not None:
            banner.onDisappear()
        return
