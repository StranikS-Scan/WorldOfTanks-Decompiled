# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/event_settings/event_settings_controller.py
from copy import deepcopy
import BigWorld
from event_settings.event_disabled_settings import EventDisabledSettings
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from helpers import dependency, aop
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IGameEventController, IEventSettingsController
from aop import PointcutDisableSettingsControls
from skeletons.prebattle_vehicle import IPrebattleVehicle

class EventSettingsController(IEventSettingsController, IGlobalListener):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __gameEventController = dependency.descriptor(IGameEventController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    _DAMAGE_INDICATOR_SETTINGS_FOR_BOSS = {'damageIndicatorType': 0,
     'damageIndicatorCrits': 1,
     'damageIndicatorAllies': 1,
     'damageIndicatorDamageValue': 0,
     'damageIndicatorDynamicIndicator': 0,
     'damageIndicatorVehicleInfo': 0,
     'damageIndicatorAnimation': 0}
    _DAMAGE_INDICATOR_SETTINGS_FOR_NONBOSS = {'damageIndicatorType': 1,
     'damageIndicatorCrits': 1,
     'damageIndicatorAllies': 1,
     'damageIndicatorDamageValue': 1,
     'damageIndicatorDynamicIndicator': 1,
     'damageIndicatorVehicleInfo': 1,
     'damageIndicatorAnimation': 1}
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
     'progressViewConditions': 1L,
     'showHPBar': 0,
     'showHPValues': 0,
     'enableTierGrouping': 0,
     'showHPDifference': 0}
    _COMMON_MARKER_VALUES = {'markerBaseIcon': 0,
     'markerAltIcon': 1,
     'markerBaseLevel': 0,
     'markerAltLevel': 0,
     'markerBaseVehicleName': 1,
     'markerAltVehicleName': 1,
     'markerBasePlayerName': 1,
     'markerAltPlayerName': 1,
     'markerBaseDamage': 1,
     'markerAltDamage': 1}
    _MARKERS = {'enemy': deepcopy(_COMMON_MARKER_VALUES),
     'ally': deepcopy(_COMMON_MARKER_VALUES),
     'dead': deepcopy(_COMMON_MARKER_VALUES)}
    _MARKERS['enemy'].update({'markerBaseHpIndicator': 1,
     'markerAltHpIndicator': 1,
     'markerBaseAimMarker2D': 1,
     'markerAltAimMarker2D': 1,
     'markerBaseHp': 1,
     'markerAltHp': 1})
    _MARKERS['ally'].update({'markerBaseHpIndicator': 1,
     'markerAltHpIndicator': 1,
     'markerBaseHp': 1,
     'markerAltHp': 1})
    _MARKERS['dead'].update({'markerBaseHpIndicator': 0,
     'markerAltHpIndicator': 1,
     'markerBaseHp': 0,
     'markerAltHp': 1})
    _ALL_EVENT_SETTINGS = {}
    _ALL_EVENT_SETTINGS.update(_DAMAGE_INDICATOR_SETTINGS_FOR_NONBOSS)
    _ALL_EVENT_SETTINGS.update(_BATTLE_EVENTS_SETTINGS)
    _ALL_EVENT_SETTINGS.update(_DAMAGE_LOG_SETTINGS)
    _ALL_EVENT_SETTINGS.update(_QUESTS_PROGRESS)
    _ALL_EVENT_SETTINGS.update(_MARKERS)
    _DISABLED_STORAGES = ('damageIndicator', 'damageLog', 'battleEvents', 'questsProgress', 'battleHud', 'markers')

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
        self.__prebattleVehicle.onChanged += self.__onCurrentVehicleChanged

    def fini(self):
        self.__weaver.clear()
        self.__weaver = None
        self.__disabledSettings = None
        self.__userSettings = None
        self.__eventSettingEnabled = False
        self.__settingsChanged = False
        self.__settingsCore.onSettingsReady -= self.__swapAfter
        self.__prebattleVehicle.onChanged -= self.__onCurrentVehicleChanged
        return

    @property
    def disabledSettings(self):
        return self.__disabledSettings.disabledSetting

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
        vehicle = BigWorld.player().vehicle
        if vehicle:
            self.__applyIndicatorSettings(vehicle.typeDescriptor.type)

    def onLobbyInited(self, event):
        self.__swapSettings()
        self.startGlobalListening()

    def onPrbEntitySwitched(self):
        self.__swapSettings()

    @property
    def __isInEvent(self):
        return self.__gameEventController.isEventPrbActive() or self.__sessionProvider.arenaVisitor.gui.isEventBattle()

    def __onCurrentVehicleChanged(self):
        vehicle = self.__prebattleVehicle.item
        if vehicle is not None:
            self.__applyIndicatorSettings(vehicle.descriptor.type)
        return

    def __applyIndicatorSettings(self, vehicleType):
        if not vehicleType or not self.__isInEvent:
            return
        isBoss = VEHICLE_TAGS.EVENT_BOSS in vehicleType.tags
        settings = self._DAMAGE_INDICATOR_SETTINGS_FOR_BOSS if isBoss else self._DAMAGE_INDICATOR_SETTINGS_FOR_NONBOSS
        self.__settingsCore.applySettings(settings)

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
            self.__settingsCore.clearStorages()
            self.__userSettings = None
        self.__eventSettingEnabled = False
        return
