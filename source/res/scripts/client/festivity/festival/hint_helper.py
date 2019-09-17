# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/festival/hint_helper.py
from account_helpers.settings_core.settings_constants import FestivalSettings
from helpers import dependency
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.festival import IFestivalController
_FEST_BUY_RANDOM_HINT_ID = 'FestivalScreenBuyRandomItem'
_FEST_OPEN_MINI_GAMES_HINT_ID = 'FestivalScreenOpenMiniGames'

class FestivalHintHelper(object):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __festController = dependency.descriptor(IFestivalController)

    @classmethod
    def getFirstEntry(cls):
        return cls.__settingsCore.serverSettings.getOnceOnlyHintsSetting(FestivalSettings.FIRST_ENTRY, True)

    @classmethod
    def setFirstEntry(cls):
        cls.__settingsCore.serverSettings.setOnceOnlyHintsSettings({FestivalSettings.FIRST_ENTRY: True})

    @classmethod
    def getBuyRandom(cls):
        return cls.__settingsCore.serverSettings.getOnceOnlyHintsSetting(FestivalSettings.BUY_RANDOM_HINT, True)

    @classmethod
    def setBuyRandom(cls):
        cls.__settingsCore.serverSettings.setOnceOnlyHintsSettings({FestivalSettings.BUY_RANDOM_HINT: True})

    @classmethod
    def canShowIsBuyRandom(cls, additionalCondition=True):
        canShowRndHint = cls.__festController.canShowRandomBtnHint()
        return additionalCondition and canShowRndHint and cls.getFirstEntry() and not cls.getBuyRandom()

    @staticmethod
    def updateRndBuyHintVisible(value):
        eventType = events.TutorialEvent.ON_COMPONENT_FOUND if value else events.TutorialEvent.ON_COMPONENT_LOST
        g_eventBus.handleEvent(events.TutorialEvent(eventType, targetID=_FEST_BUY_RANDOM_HINT_ID), scope=EVENT_BUS_SCOPE.GLOBAL)

    @classmethod
    def getMiniGames(cls):
        return cls.__settingsCore.serverSettings.getOnceOnlyHintsSetting(FestivalSettings.MINI_GAMES, True)

    @classmethod
    def setMiniGames(cls):
        cls.__settingsCore.serverSettings.setOnceOnlyHintsSettings({FestivalSettings.MINI_GAMES: True})

    @classmethod
    def canShowMiniGames(cls):
        return cls.getFirstEntry() and cls.getBuyRandom() and not cls.getMiniGames() and cls.__festController.isMiniGamesEnabled()

    @staticmethod
    def updateMiniGamesHintVisible(value):
        eventType = events.TutorialEvent.ON_COMPONENT_FOUND if value else events.TutorialEvent.ON_COMPONENT_LOST
        g_eventBus.handleEvent(events.TutorialEvent(eventType, targetID=_FEST_OPEN_MINI_GAMES_HINT_ID), scope=EVENT_BUS_SCOPE.GLOBAL)
