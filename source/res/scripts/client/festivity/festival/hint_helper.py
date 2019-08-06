# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/festival/hint_helper.py
from account_helpers.settings_core.settings_constants import FestivalSettings
from helpers import dependency
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.festival import IFestivalController
_FEST_BUY_RANDOM_HINT_ID = 'FestivalScreenBuyRandomItem'

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
