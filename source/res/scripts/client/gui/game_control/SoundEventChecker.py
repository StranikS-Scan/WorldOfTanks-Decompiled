# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/SoundEventChecker.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.app_loader.decorators import sf_lobby
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.money import Money, Currency, ZERO_MONEY
from helpers import dependency
from skeletons.gui.game_control import ISoundEventChecker
from skeletons.gui.shared import IItemsCache
_SPEND_SINGLE_SOUNDS = {Currency.CREDITS: SoundEffectsId.SPEND_CREDITS,
 Currency.GOLD: SoundEffectsId.SPEND_CREDITS,
 Currency.CRYSTAL: SoundEffectsId.SPEND_CRYSTAL}
_EARN_SINGLE_SOUNDS = {Currency.CREDITS: SoundEffectsId.EARN_CREDITS,
 Currency.GOLD: SoundEffectsId.EARN_CREDITS,
 Currency.CRYSTAL: SoundEffectsId.EARN_CRYSTAL}
_SPEND_MULTI_SOUNDS = {(Currency.CREDITS, Currency.GOLD): SoundEffectsId.SPEND_CREDITS_GOLD}
_EARN_MULTI_SOUNDS = {(Currency.CREDITS, Currency.GOLD): SoundEffectsId.EARN_CREDITS_GOLD}

class SoundEventChecker(ISoundEventChecker):
    """Client event checker. Plays sounds for some events type."""
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(SoundEventChecker, self).__init__()
        self.__currentMoney = ZERO_MONEY

    @sf_lobby
    def app(self):
        return None

    def onLobbyStarted(self, ctx):
        self.__currentMoney = self.itemsCache.items.stats.money.copy()
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
        newValues = Money.extractMoneyDict(stats)
        if newValues:
            spendCurrencies = []
            earnCurrencies = []
            for currency, value in newValues.iteritems():
                if value < self.__currentMoney.get(currency):
                    spendCurrencies.append(currency)
                if value > self.__currentMoney.get(currency):
                    earnCurrencies.append(currency)

            if spendCurrencies:
                self.__playSound(self.__getSoundID(spendCurrencies, _SPEND_SINGLE_SOUNDS, _SPEND_MULTI_SOUNDS, SoundEffectsId.SPEND_DEFAULT_SOUND))
            elif earnCurrencies:
                self.__playSound(self.__getSoundID(earnCurrencies, _EARN_SINGLE_SOUNDS, _EARN_MULTI_SOUNDS, SoundEffectsId.EARN_DEFAULT_SOUND))
            self.__currentMoney = self.__currentMoney.replaceAll(newValues)

    @classmethod
    def __getSoundID(cls, currencies, singleSounds, multiSounds, defSound):
        if len(currencies) == 1:
            return singleSounds.get(currencies[0], defSound)
        currencies = set(currencies)
        for k, soundID in multiSounds:
            if set(k) == currencies:
                return soundID

        return defSound
