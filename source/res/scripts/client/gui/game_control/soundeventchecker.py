# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/SoundEventChecker.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.app_loader.decorators import sf_lobby
from gui.shared import g_itemsCache
from gui.shared.SoundEffectsId import SoundEffectsId
from skeletons.gui.game_control import ISoundEventChecker

class SoundEventChecker(ISoundEventChecker):

    def __init__(self):
        super(SoundEventChecker, self).__init__()
        self.__credits, self.__gold = (0, 0)

    @sf_lobby
    def app(self):
        return None

    def onLobbyStarted(self, ctx):
        money = g_itemsCache.items.stats.money
        self.__credits = money.credits
        self.__gold = money.gold
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
        app = self.app
        if app is not None and app.soundManager is not None:
            app.soundManager.playEffectSound(soundName)
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
