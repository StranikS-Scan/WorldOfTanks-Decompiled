# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/event_settings/event_settings_swapper.py
from helpers import dependency, aop
import PlayerEvents
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IRacingEventController
from skeletons.gui.battle_session import IBattleSessionProvider
from event_disabled_settings import EventDisabledSettings
from aop import _PointcutDisableSettingsControls, _PointcutApplyOnlyUserSettings, _PointcutApplyUnchangedSettings

class EventSettingsSwapper(object):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _racingEventController = dependency.descriptor(IRacingEventController)
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _MARKER_SETTINGS = {'enemy': {'markerBaseHp': 0,
               'markerBasePlayerName': 0,
               'markerAltPlayerName': 1,
               'markerBaseHpIndicator': 1,
               'markerAltHpIndicator': 1,
               'markerBaseIcon': 0,
               'markerBaseDamage': 1,
               'markerBaseVehicleName': 1,
               'markerAltIcon': 0,
               'markerBaseLevel': 0,
               'markerAltDamage': 1,
               'markerAltVehicleName': 1,
               'markerAltLevel': 0,
               'markerAltHp': 1L,
               'markerBaseAimMarker2D': 1,
               'markerAltAimMarker2D': 1},
     'dead': {'markerBaseHp': 3,
              'markerBasePlayerName': 0,
              'markerAltPlayerName': 1,
              'markerBaseHpIndicator': 0,
              'markerAltHpIndicator': 0,
              'markerBaseIcon': 0,
              'markerBaseDamage': 1,
              'markerBaseVehicleName': 1,
              'markerAltIcon': 0,
              'markerBaseLevel': 0,
              'markerAltDamage': 1,
              'markerAltVehicleName': 1,
              'markerAltLevel': 0,
              'markerAltHp': 3L},
     'ally': {'markerBaseHp': 0,
              'markerBasePlayerName': 0,
              'markerAltPlayerName': 1,
              'markerBaseHpIndicator': 1,
              'markerAltHpIndicator': 1,
              'markerBaseIcon': 0,
              'markerBaseDamage': 1,
              'markerBaseVehicleName': 1,
              'markerAltIcon': 0,
              'markerBaseLevel': 0,
              'markerAltDamage': 1,
              'markerAltVehicleName': 1,
              'markerAltLevel': 0,
              'markerAltHp': 1L}}
    _DAMAGE_INDICATOR_SETTINGS = {'damageIndicatorType': 0,
     'damageIndicatorVehicleInfo': 0,
     'damageIndicatorDamageValue': 0,
     'damageIndicatorAnimation': 0,
     'damageIndicatorDynamicIndicator': 0,
     'damageIndicatorPresets': 0}
    _AIM_SETTINGS = {'arcade': {'reloaderTimer': 0L,
                'gunTagType': 9,
                'centralTag': 100,
                'gunTag': 100,
                'centralTagType': 10L,
                'mixingType': 3L,
                'netType': 0,
                'net': 0,
                'mixing': 100,
                'cassette': 100,
                'reloader': 0,
                'zoomIndicator': 100,
                'condition': 0},
     'sniper': {'reloaderTimer': 0L,
                'gunTagType': 9,
                'centralTag': 100,
                'gunTag': 100,
                'centralTagType': 10L,
                'mixingType': 3L,
                'netType': 0,
                'net': 0,
                'mixing': 100,
                'cassette': 100,
                'reloader': 0,
                'zoomIndicator': 100,
                'condition': 0}}
    _BATTLE_EVENTS_SETTINGS = {'battleEventsEnemyBurning': 0,
     'battleEventsEnemyWorldCollision': 0,
     'battleEventsBaseCapture': 1,
     'battleEventsEnemyCriticalHit': 0,
     'battleEventsBaseCaptureDrop': 0,
     'battleEventsReceivedDamage': 1,
     'battleEventsEnemyAssistStun': 0,
     'battleEventsEnemyRamAttack': 1,
     'battleEventsShowInBattle': 1,
     'battleEventsEnemyKill': 1,
     'battleEventsVehicleInfo': 1,
     'battleEventsEnemyHpDamage': 1,
     'battleEventsEnemyDetection': 0,
     'battleEventsEnemyDetectionDamage': 0,
     'battleEventsEnemyTrackDamage': 0,
     'battleEventsBlockedDamage': 1,
     'battleEventsReceivedCrits': 0,
     'battleEventsEventName': 1}
    _DAMAGE_LOG_SETTINGS = {'damageLogShowDetails': 2,
     'damageLogShowEventTypes': 0,
     'damageLogAssistStun': 0,
     'damageLogEventsPosition': 0,
     'damageLogAssistDamage': 0,
     'damageLogBlockedDamage': 1,
     'damageLogTotalDamage': 1}
    _GAME_SETTINGS = {'minimapMaxViewRange': 0,
     'minimapViewRange': 0,
     'showVectorOnMap': 0,
     'minimapDrawRange': 0,
     'dynamicCamera': 0}
    _QUESTS_PROGRESS = {'progressViewType': 1L}
    _ALL_EVENT_SETTINGS = {}
    _ALL_EVENT_SETTINGS.update(_MARKER_SETTINGS)
    _ALL_EVENT_SETTINGS.update(_DAMAGE_INDICATOR_SETTINGS)
    _ALL_EVENT_SETTINGS.update(_AIM_SETTINGS)
    _ALL_EVENT_SETTINGS.update(_BATTLE_EVENTS_SETTINGS)
    _ALL_EVENT_SETTINGS.update(_DAMAGE_LOG_SETTINGS)
    _ALL_EVENT_SETTINGS.update(_GAME_SETTINGS)
    _ALL_EVENT_SETTINGS.update(_QUESTS_PROGRESS)

    def __init__(self):
        self.__userSettings = None
        self.__settingsChanged = True
        self.__disabledSettings = None
        self.__weaver = None
        return

    def init(self):
        self.__addListeners()
        self.__disabledSettings = EventDisabledSettings()
        self.__weaver = aop.Weaver()

    def fini(self):
        self.__removeListeners()
        self.__weaver.clear()
        self.__weaver = None
        self.__disabledSettings = None
        self.__userSettings = None
        return

    @property
    def disabledSettings(self):
        return self.__disabledSettings.disabledSetting

    def __addListeners(self):
        self._settingsCore.onStoragesCleared += self.__onSettingStoragesCleared
        self._settingsCore.onSettingsApplied += self.__onSettingsApplied
        self._racingEventController.onEventModeChanged += self.__swapSettings
        PlayerEvents.g_playerEvents.onAvatarBecomePlayer += self.__onAvatarBecomePlayer

    def __removeListeners(self):
        self._settingsCore.onStoragesCleared -= self.__onSettingStoragesCleared
        self._settingsCore.onSettingsApplied -= self.__onSettingsApplied
        self._racingEventController.onEventModeChanged -= self.__swapSettings
        PlayerEvents.g_playerEvents.onAvatarBecomePlayer -= self.__onAvatarBecomePlayer

    def __onSettingsApplied(self, _):
        self.__settingsChanged = not self.__isInEvent

    def __onAvatarBecomePlayer(self):
        if self.__userSettings is None and self._sessionProvider.arenaVisitor.gui.isEventBattle():
            self.__swapSettings(True)
        return

    def __onSettingStoragesCleared(self):
        if self.__isInEvent:
            self.__swapSettings(True)

    @property
    def __isInEvent(self):
        return self._racingEventController.isEventModeOn() or self._sessionProvider.arenaVisitor.gui.isEventBattle()

    def __swapSettings(self, isEventModeOn):
        if isEventModeOn:
            if self.__settingsChanged:
                self.__userSettings = {setting:self._settingsCore.getSetting(setting) for setting in self._ALL_EVENT_SETTINGS}
                self.__settingsChanged = False
            if self.__weaver.findPointcut(_PointcutApplyUnchangedSettings) == -1:
                self.__weaver.weave(pointcut=_PointcutApplyUnchangedSettings)
            self._settingsCore.applySettings(self._ALL_EVENT_SETTINGS)
            if self.__weaver.findPointcut(_PointcutDisableSettingsControls) == -1:
                self.__weaver.weave(pointcut=_PointcutDisableSettingsControls)
                self.__weaver.weave(pointcut=_PointcutApplyOnlyUserSettings)
        elif self.__userSettings is not None:
            self.__weaver.clear()
            self._settingsCore.applySettings(self.__userSettings)
        return


g_instance = EventSettingsSwapper()
