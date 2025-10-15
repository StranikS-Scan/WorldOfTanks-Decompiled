# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/portal_event_helpers.py
from gui import GUI_SETTINGS
import CGF
from skeletons.gui.shared.utils import IHangarSpace
from helpers import dependency
from Queue import Queue
from functools import wraps
import BigWorld
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getPortalShopUrl
from th_async import th_async, th_await, delay
PROGRESSION_QUEST_PREFIX = 'portal:progression:'
LAST_LEVEL_QUEST = 'portal:last_level_victory'
ALL_VEHICLES_UPGRADED_QUEST_ID = 'portal:all_vehicles_upgraded'

def getInfoPageURL():
    return GUI_SETTINGS.portalInfoPageURL


def getShopPageURL():
    return getPortalShopUrl()


def isPortalProgressionQuest(questId):
    return questId.startswith(PROGRESSION_QUEST_PREFIX)


def isPortalLastLevelQuest(questId):
    return questId.startswith(LAST_LEVEL_QUEST)


def isPortalAllVehicleUpgradesQuest(questId):
    return questId.startswith(ALL_VEHICLES_UPGRADED_QUEST_ID)


class ExecuteAfterCondition(object):
    __slots__ = ('__queue', '__callbackID')

    def __init__(self):
        self.__queue = Queue()
        self.__callbackID = None
        return

    def __call__(self, func):

        @wraps(func)
        def wrapped(*args, **kwargs):
            self._enqueueCall(func, *args, **kwargs)
            if self.__callbackID is None:
                self._checkCondition()
            return

        return wrapped

    @property
    def condition(self):
        raise NotImplementedError

    def _checkCondition(self):
        if not self.condition:
            self.__callbackID = BigWorld.callback(0.0, self._checkCondition)
            return
        else:
            self.__callbackID = None
            self._executeEnqueuedCalls()
            return

    def _enqueueCall(self, func, *args, **kwargs):
        self.__queue.put((func, args, kwargs))

    def _executeEnqueuedCalls(self):
        while not self.__queue.empty():
            f, args, kwargs = self.__queue.get()
            f(*args, **kwargs)


class ExecuteAfterAllEventVehiclesLoaded(ExecuteAfterCondition):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    @property
    def condition(self):
        if not self.__hangarSpace.spaceInited:
            return False
        else:
            space = self.__hangarSpace.space
            if space is None:
                return False
            from HangarVehicle import HangarVehicle
            query = CGF.Query(space.getSpaceID(), HangarVehicle)
            if query.empty():
                return False
            allVehicleLoaded = all([ vehicle.model is not None for vehicle in query.values() ])
            return allVehicleLoaded


EXECUTE_AFTER_ALL_EVENT_VEHICLES_LOADED = ExecuteAfterAllEventVehiclesLoaded()

class PortalBinocularsMode(object):
    GUIDED_MISSILE = 'guidedMissile'
    VEHICLE_CHANGE = 'vehicleChange'
    BERSERK = 'berserk'


class useFadingBinocular(object):

    def __init__(self, binocularsMode):
        super(useFadingBinocular, self).__init__()
        self.__binocularsMode = binocularsMode

    def __call__(self, func):

        @wraps(func)
        @th_async
        def wrapper(*args, **kwargs):
            binoculars = BigWorld.binoculars()
            if not binoculars:
                func(*args, **kwargs)
                return
            fadeTime = 0.0
            if self.__binocularsMode == PortalBinocularsMode.GUIDED_MISSILE:
                fadeTime = binoculars.getPTURFadeTime()
                state = binoculars.getIsPTUR()
                binoculars.setIsPTUR(not state)
            elif self.__binocularsMode == PortalBinocularsMode.VEHICLE_CHANGE:
                fadeTime = binoculars.getPossessionFadeTime()
                state = binoculars.getIsPossession()
                binoculars.setIsPossession(not state)
            yield th_await(delay(fadeTime))
            func(*args, **kwargs)

        return wrapper
