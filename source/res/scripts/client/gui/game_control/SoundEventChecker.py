# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/SoundEventChecker.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.app_loader import sf_lobby
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.money import Money, Currency, MONEY_UNDEFINED
from helpers import dependency
from skeletons.gui.game_control import ISoundEventChecker
from skeletons.gui.shared import IItemsCache
_SPEND_SINGLE_SOUNDS = {Currency.CREDITS: SoundEffectsId.SPEND_CREDITS,
 Currency.GOLD: SoundEffectsId.SPEND_CREDITS,
 Currency.CRYSTAL: SoundEffectsId.SPEND_CRYSTAL,
 Currency.EVENT_COIN: SoundEffectsId.SPEND_EVENT_COIN}
_EARN_SINGLE_SOUNDS = {Currency.CREDITS: SoundEffectsId.EARN_CREDITS,
 Currency.GOLD: SoundEffectsId.EARN_CREDITS,
 Currency.CRYSTAL: SoundEffectsId.EARN_CRYSTAL,
 Currency.EVENT_COIN: SoundEffectsId.EARN_EVENT_COIN}
_SPEND_MULTI_SOUNDS = {(Currency.CREDITS, Currency.GOLD): SoundEffectsId.SPEND_CREDITS_GOLD}
_EARN_MULTI_SOUNDS = {(Currency.CREDITS, Currency.GOLD): SoundEffectsId.EARN_CREDITS_GOLD}

class SoundEventChecker(ISoundEventChecker):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(SoundEventChecker, self).__init__()
        self.__currentMoney = MONEY_UNDEFINED
        self.__isLocked = False
        self.__spendCurrencies = []
        self.__earnCurrencies = []

    @sf_lobby
    def app(self):
        return None

    def onLobbyStarted(self, ctx):
        self.__currentMoney = self.itemsCache.items.stats.money.copy()
        g_clientUpdateManager.addCallbacks({'stats': self.__onStatsChanged})

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()

    def lockPlayingSounds(self):
        self.__isLocked = True

    def unlockPlayingSounds(self):
        self.__isLocked = False
        self.__playAllSounds()

    def __stop(self):
        self.__isLocked = False
        self.__spendCurrencies = []
        self.__earnCurrencies = []
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __playSound(self, soundName):
        app = self.app
        if app is not None and app.soundManager is not None:
            app.soundManager.playEffectSound(soundName)
        return

    def __playAllSounds(self):
        if self.__spendCurrencies:
            self.__playSound(self.__getSoundID(self.__spendCurrencies, _SPEND_SINGLE_SOUNDS, _SPEND_MULTI_SOUNDS, SoundEffectsId.SPEND_DEFAULT_SOUND))
        elif self.__earnCurrencies:
            self.__playSound(self.__getSoundID(self.__earnCurrencies, _EARN_SINGLE_SOUNDS, _EARN_MULTI_SOUNDS, SoundEffectsId.EARN_DEFAULT_SOUND))
        self.__spendCurrencies = []
        self.__earnCurrencies = []

    def __onStatsChanged(self, stats):
        newValues = Money.extractMoneyDict(stats)
        if newValues:
            for currency, value in newValues.iteritems():
                if value < self.__currentMoney.get(currency, 0):
                    self.__spendCurrencies.append(currency)
                if value > self.__currentMoney.get(currency, 0):
                    self.__earnCurrencies.append(currency)

            if not self.__isLocked:
                self.__playAllSounds()
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
