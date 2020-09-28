# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/event_settings/event_settings_controller.py
from event_settings.event_disabled_settings import EventDisabledSettings
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency, aop
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IGameEventController, IEventSettingsController
from aop import PointcutDisableSettingsControls

class EventSettingsController(IEventSettingsController, IGlobalListener):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __gameEventController = dependency.descriptor(IGameEventController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _DAMAGE_INDICATOR_SETTINGS = {'damageIndicatorType': 0,
     'damageIndicatorVehicleInfo': 0,
     'damageIndicatorDamageValue': 0,
     'damageIndicatorAnimation': 0,
     'damageIndicatorDynamicIndicator': 0,
     'damageIndicatorCrits': 1,
     'damageIndicatorAllies': 1}
    _BATTLE_EVENTS_SETTINGS = {'battleEventsEnemyBurning': 1,
     'battleEventsEnemyWorldCollision': 1,
     'battleEventsBaseCapture': 0,
     'battleEventsEnemyCriticalHit': 1,
     'battleEventsBaseCaptureDrop': 0,
     'battleEventsReceivedDamage': 1,
     'battleEventsEnemyAssistStun': 0,
     'battleEventsEnemyRamAttack': 1,
     'battleEventsShowInBattle': 1,
     'battleEventsEnemyKill': 1,
     'battleEventsVehicleInfo': 1,
     'battleEventsEnemyHpDamage': 1,
     'battleEventsEnemyDetection': 1,
     'battleEventsEnemyDetectionDamage': 1,
     'battleEventsEnemyTrackDamage': 1,
     'battleEventsBlockedDamage': 1,
     'battleEventsReceivedCrits': 1,
     'battleEventsEventName': 1,
     'battleEventsEnemyStun': 0}
    _DAMAGE_LOG_SETTINGS = {'damageLogShowDetails': 2,
     'damageLogShowEventTypes': 0,
     'damageLogAssistStun': 0,
     'damageLogEventsPosition': 0,
     'damageLogAssistDamage': 1,
     'damageLogBlockedDamage': 1,
     'damageLogTotalDamage': 1}
    _QUESTS_PROGRESS = {'progressViewType': 1L,
     'progressViewConditions': 1L}
    _ALL_EVENT_SETTINGS = {}
    _ALL_EVENT_SETTINGS.update(_DAMAGE_INDICATOR_SETTINGS)
    _ALL_EVENT_SETTINGS.update(_BATTLE_EVENTS_SETTINGS)
    _ALL_EVENT_SETTINGS.update(_DAMAGE_LOG_SETTINGS)
    _ALL_EVENT_SETTINGS.update(_QUESTS_PROGRESS)
    _DISABLED_STORAGES = ('damageIndicator', 'damageLog', 'battleEvents', 'questsProgress')

    def __init__(self):
        self.__userSettings = None
        self.__disabledSettings = None
        self.__weaver = None
        self.__eventSettingEnabled = False
        self.__settingsChanged = False
        return

    def init(self):
        self.__disabledSettings = EventDisabledSettings()
        self.__weaver = aop.Weaver()

    def fini(self):
        self.__weaver.clear()
        self.__weaver = None
        self.__disabledSettings = None
        self.__userSettings = None
        self.__eventSettingEnabled = False
        self.__settingsChanged = False
        return

    @property
    def disabledSettings(self):
        return self.__disabledSettings.disabledSetting

    def getSetting(self, key, default=None):
        return self._ALL_EVENT_SETTINGS.get(key, default)

    def onDisconnected(self):
        self.stopGlobalListening()
        if self.__weaver is not None:
            self.__weaver.clear()
        if self.__userSettings is not None:
            self.__settingsCore.unsetEventDisabledStorages()
            self.__settingsCore.clearStorages()
            self.__userSettings = None
        self.__eventSettingEnabled = False
        return

    def onAvatarBecomePlayer(self):
        self.stopGlobalListening()
        self.__swapSettings()

    def onLobbyInited(self, event):
        self.__swapSettings()
        self.startGlobalListening()

    def onPrbEntitySwitched(self):
        self.__swapSettings()

    @property
    def __isInEvent(self):
        return self.__gameEventController.isEventPrbActive() or self.__sessionProvider.arenaVisitor.gui.isEventBattle()

    def __swapSettings(self):
        if not self.__settingsCore.isReady:
            self.__settingsCore.onSettingsReady += self.__swapAfter
            return
        if self.__isInEvent == self.__eventSettingEnabled:
            return
        if self.__isInEvent:
            self.__disable()
        else:
            self.__enable()

    def __swapAfter(self):
        self.__settingsCore.onSettingsReady -= self.__swapAfter
        self.__swapSettings()

    def __disable(self):
        self.__userSettings = {setting:self.__settingsCore.getSetting(setting) for setting in self._ALL_EVENT_SETTINGS}
        self.__settingsCore.setEventDisabledStorages(self._DISABLED_STORAGES)
        self.__settingsCore.applySettings(self._ALL_EVENT_SETTINGS)
        if self.__weaver.findPointcut(PointcutDisableSettingsControls) == -1:
            self.__weaver.weave(pointcut=PointcutDisableSettingsControls)
        self.__eventSettingEnabled = True

    def __enable(self):
        if self.__weaver is not None:
            self.__weaver.clear()
        if self.__userSettings is not None:
            self.__settingsCore.unsetEventDisabledStorages()
            self.__settingsCore.applySettings(self.__userSettings)
            self.__userSettings = None
        self.__eventSettingEnabled = False
        return
