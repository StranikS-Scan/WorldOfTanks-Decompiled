# Embedded file name: scripts/client/gui/game_control/SoundEventChecker.py
from gui.app_loader.decorators import sf_lobby
from gui.game_control.controllers import Controller
from gui.shared import g_itemsCache
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.SoundEffectsId import SoundEffectsId

class SoundEventChecker(Controller):

    def __init__(self, proxy):
        super(SoundEventChecker, self).__init__(proxy)
        self.__credits, self.__gold = (0, 0)

    @sf_lobby
    def app(self):
        return None

    def onLobbyStarted(self, ctx):
        self.__credits, self.__gold = g_itemsCache.items.stats.money
        g_clientUpdateManager.addCallbacks({'stats': self.__onStatsChanged})
        from CurrentVehicle import g_currentVehicle
        g_currentVehicle.onChangeStarted += self.__onVehicleChanging

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()

    def __stop(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        from CurrentVehicle import g_currentVehicle
        g_currentVehicle.onChangeStarted -= self.__onVehicleChanging

    def __playSound(self, soundName):
        if self.app.soundManager is not None:
            self.app.soundManager.playEffectSound(soundName)
        return

    def __onVehicleChanging(self):
        self.__playSound('effects.vehicle_changing')

    def __onStatsChanged(self, stats):
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
