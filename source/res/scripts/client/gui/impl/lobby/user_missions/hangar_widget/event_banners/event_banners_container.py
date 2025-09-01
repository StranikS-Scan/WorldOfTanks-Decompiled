# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/event_banners/event_banners_container.py
import typing
import Event
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Dict, Type
    from base_event_banner import BaseEventBanner

class _Singleton(type):
    __instance = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls.__instance


class EventBannersContainer(object):
    __metaclass__ = _Singleton
    __slots__ = ('__eventsMap', 'onBannerUpdate')

    def __init__(self):
        self.onBannerUpdate = Event.Event()
        self.__eventsMap = {}

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
