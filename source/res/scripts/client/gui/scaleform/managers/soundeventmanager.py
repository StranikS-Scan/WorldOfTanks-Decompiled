# Embedded file name: scripts/client/gui/Scaleform/managers/SoundEventManager.py
from gui.Scaleform.framework import AppRef
from gui.ClientUpdateManager import g_clientUpdateManager
from CurrentVehicle import g_currentVehicle
from gui.shared.SoundEffectsId import SoundEffectsId

class SoundEventManager(AppRef):

    def __init__(self, credits = 0, gold = 0):
        self.__credits = credits
        self.__gold = gold
        g_clientUpdateManager.addCallbacks({'stats': self.onStatsChanged})
        g_currentVehicle.onChangeStarted += self.onVehicleChanging

    def cleanUp(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChangeStarted -= self.onVehicleChanging

    def __playSound(self, soundName):
        if self.app.soundManager is not None:
            self.app.soundManager.playEffectSound(soundName)
        return

    def onVehicleChanging(self):
        """ Current vehicle starts changing event handler """
        self.__playSound('effects.vehicle_changing')

    def onStatsChanged(self, stats):
        """ Client stats changed event handler """
        newCredits = stats.get('credits', self.__credits)
        newGold = stats.get('gold', self.__gold)
        if newCredits < self.__credits and newGold < self.__gold:
            self.__playSound(SoundEffectsId.SPEND_CREDITS_GOLD)
        elif newCredits > self.__credits and newGold > self.__gold:
            self.__playSound(SoundEffectsId.EARN_CREDITS_GOLD)
        elif newCredits < self.__credits:
            self.__playSound(SoundEffectsId.SPEND_CREDITS)
        elif newCredits > self.__credits:
            self.__playSound(SoundEffectsId.EARN_CREDITS)
        elif newGold < self.__gold:
            self.__playSound(SoundEffectsId.SPEND_GOLD)
        elif newGold > self.__gold:
            self.__playSound(SoundEffectsId.EARN_GOLD)
        self.__credits, self.__gold = newCredits, newGold
