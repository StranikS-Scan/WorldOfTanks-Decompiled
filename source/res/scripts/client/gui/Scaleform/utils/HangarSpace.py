# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/utils/HangarSpace.py
# Compiled at: 2011-03-31 19:57:51
from gui.ClientHangarSpace import ClientHangarSpace
from gui.Scaleform.Waiting import Waiting
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG
from Event import Event, EventManager
import BigWorld

class _HangarSpace(object):

    def __init__(self):
        self.__space = ClientHangarSpace()
        self.__inited = False
        self.__isSpacePremium = False
        self.__spaceInited = False
        self.__delayedRefreshCallback = None
        self.__delayedIsPremium = False
        self.__spaceDestroyedDuringLoad = False
        return

    @property
    def space(self):
        if self.spaceInited:
            return self.__space
        else:
            return None

    @property
    def inited(self):
        return self.__inited

    @property
    def spaceInited(self):
        return self.__spaceInited

    def spaceLoading(self):
        return self.__space.spaceLoading()

    def init(self, isPremium):
        if not self.spaceInited:
            LOG_DEBUG('_HangarSpace::init')
            Waiting.show('loadHangarSpace')
            self.__inited = True
            self.__isSpacePremium = isPremium
            self.__space.create(isPremium, self.__spaceDone)
            g_currentVehicle.onChanged += self.refreshVehicle
            self.refreshVehicle()

    def refreshSpace(self, isPremium):
        if not self.__spaceInited:
            LOG_DEBUG('_HangarSpace::refreshSpace(isPremium=' + str(isPremium) + ') - is delayed until space load is done')
            if self.__delayedRefreshCallback is None:
                self.__delayedRefreshCallback = BigWorld.callback(0.1, self.__delayedRefresh)
            self.__delayedIsPremium = isPremium
            return
        else:
            LOG_DEBUG('_HangarSpace::refreshSpace(isPremium=' + str(isPremium) + ')')
            if self.__isSpacePremium != isPremium:
                self.destroy()
                self.init(isPremium)
            self.__isSpacePremium = isPremium
            return

    def destroy(self):
        if self.spaceInited:
            LOG_DEBUG('_HangarSpace::destroy')
            self.__inited = False
            self.__spaceInited = False
            self.__space.destroy()
            g_currentVehicle.onChanged -= self.refreshVehicle
        elif self.spaceLoading():
            LOG_DEBUG('_HangarSpace::destroy - delayed until space load done')
            self.__spaceDestroyedDuringLoad = True
        if self.__delayedRefreshCallback is not None:
            BigWorld.cancelCallback(self.__delayedRefreshCallback)
            self.__delayedRefreshCallback = None
        return

    def refreshVehicle(self):
        if self.__inited:
            Waiting.show('loadHangarSpaceVehicle', True)
            if g_currentVehicle.isPresent() and g_currentVehicle.getState():
                self.__space.recreateVehicle(g_currentVehicle.vehicle.descriptor, g_currentVehicle.getState(), self.__changeDone)
            else:
                self.__space.removeVehicle()
                self.__changeDone()

    def __spaceDone(self):
        self.__spaceInited = True
        if self.__spaceDestroyedDuringLoad:
            self.__spaceDestroyedDuringLoad = False
            self.destroy()
        Waiting.hide('loadHangarSpace')

    def __changeDone(self):
        Waiting.hide('loadHangarSpaceVehicle')

    def __delayedRefresh(self):
        self.__delayedRefreshCallback = None
        if not self.__spaceInited:
            self.__delayedRefreshCallback = BigWorld.callback(0.1, self.__delayedRefresh)
            return
        else:
            self.refreshSpace(self.__delayedIsPremium)
            return


g_hangarSpace = _HangarSpace()
