# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/battle_upgrade_panel.py
from __future__ import absolute_import
import logging
import typing
import BigWorld
import BattleReplay
import CommandMapping as CM
from halloween.gui.scaleform.daapi.view.battle.anomalies_utils import selectAnomaly, isAnomalyNew
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import AnomaliesSounds
from halloween.skeletons.halloween_anomalies_controller import IHalloweenAnomaliesController
from shared_utils import first
from ReplayEvents import g_replayEvents
from frameworks.wulf import WindowLayer
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider
from gui import InputHandler, makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from halloween.gui.scaleform.daapi.view.meta.HWBattleUpgradePanelMeta import HWBattleUpgradePanelMeta
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.Scaleform.daapi.view.common.keybord_helpers import getHotKeyList, getHotKeysInfo
from halloween.gui.scaleform.daapi.view.battle.anomalies_utils import isAnomalyInCombo, anomalyDescriptionList, anomalyTitle
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from VehicleRespawnComponent import VehicleRespawnComponent
if typing.TYPE_CHECKING:
    from typing import Optional, List
    from gui.Scaleform.daapi.view.battle.shared import SharedPage
logger = logging.getLogger(__name__)
ICONS_PATH = R.images.halloween.gui.maps.icons.anomalies.s_58x58
_KEYS_INFO = [[CM.CMD_CM_VEHICLE_UPGRADE_PANEL_LEFT, CM.CMD_CM_VEHICLE_UPGRADE_PANEL_ALTERNATIVE_LEFT], [CM.CMD_CM_VEHICLE_UPGRADE_PANEL_RIGHT, CM.CMD_CM_VEHICLE_UPGRADE_PANEL_ALTERNATIVE_RIGHT]]
REASON_EMPTY = -1

class _AttentionEffectPlayer(object):
    __slots__ = ('__viewRef', '__callbackID', '__delayTime', '__isPlaying')
    _SHOW_DELAY = 60

    def __init__(self, viewRef):
        super(_AttentionEffectPlayer, self).__init__()
        self.__viewRef = viewRef
        self.__callbackID = None
        self.__delayTime = self._SHOW_DELAY
        self.__isPlaying = False
        return

    def setVisible(self, visible):
        if visible:
            if self.__callbackID is not None or self.__isPlaying:
                self.__stopEffect()
            self.__startTimer()
        else:
            self.__stopEffect()
        return

    def destroy(self):
        self.__viewRef = None
        self.__disposeTimer()
        return

    def __startTimer(self):
        self.__callbackID = BigWorld.callback(self.__delayTime, self.__onDelayFinished)

    def __disposeTimer(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __stopAnimation(self):
        if self.__isPlaying:
            self.__viewRef.as_hideNotificationAnimS()
            self.__isPlaying = False

    def __stopEffect(self):
        self.__disposeTimer()
        self.__stopAnimation()

    def __onDelayFinished(self):
        self.__callbackID = None
        self.__isPlaying = True
        self.__viewRef.as_showNotificationAnimS()
        return


_EMPTY_BTN_LABEL = '...'
_EMPTY_BTN_V_KEY = 'NONE'

def _getAnomaliesMatrixHotkey():
    keyInfo = getHotKeysInfo(CM.CMD_QUEST_PROGRESS_SHOW)[0].asDict()
    return {'vKey': _EMPTY_BTN_LABEL,
     'keyName': _EMPTY_BTN_LABEL} if keyInfo.get('vKey') == _EMPTY_BTN_V_KEY else keyInfo


class HWBattleUpgradePanel(HWBattleUpgradePanelMeta, IArenaVehiclesController):
    __slots__ = ('__upgrades', '__localVisible', '__attentionEffect')
    appLoader = dependency.descriptor(IAppLoader)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    hwAnomaliesCtrl = dependency.descriptor(IHalloweenAnomaliesController)
    TEXT_PATH_PANEL_INFO = R.strings.halloween_battle.upgradePanel
    _IN_COMBAT_DELAY = 1
    _COOLDOWN_DELAY = 5
    _EPIC_ANOMALY_TYPE = 'epic'

    def __init__(self):
        super(HWBattleUpgradePanel, self).__init__()
        self.__attentionEffect = _AttentionEffectPlayer(self)
        self.__localVisible = False
        self.__textInited = False
        self.__callbackDelayer = CallbackDelayer()
        self.__keyInfoList = [ [ keyInfo.asDict() for keyInfo in getHotKeysInfo(first(cmdList)) ] for cmdList in _KEYS_INFO ]
        self.__lockReason = REASON_EMPTY

    @property
    def hwBattleGuiCtrl(self):
        return self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    @property
    def upgradeOptions(self):
        return self.hwBattleGuiCtrl.currentUpgradeOptions

    def onSelectItem(self, itemID):
        selectAnomaly(itemID)

    def onAppear(self):
        playSound(AnomaliesSounds.Battle.UPGRADE_PANEL_APPEAR)

    def onItemHover(self):
        playSound(AnomaliesSounds.Battle.ITEM_HOVER)

    def _populate(self):
        super(HWBattleUpgradePanel, self)._populate()
        VehicleRespawnComponent.onVehicleRespawned += self._onVehicleRespawned
        vehicleStateCtrl = self.sessionProvider.shared.vehicleState
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart += self.__onReplayTimeWarpStart
        isVisible = False
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            if self.upgradeOptions:
                isVisible = True
            hwBattleGuiCtrl.onUpgradeOptionsUpdated += self.__updateUpgrades
            hwBattleGuiCtrl.onChangeAnomaliesViewVisibility += self.__onChangeAnomaliesViewVisibility
            hwBattleGuiCtrl.onSelectAnomaly += self.__onSelectAnomaly
        self.as_setVisibleS(isVisible)
        InputHandler.g_instance.onKeyDown += self.__handleKeyEvent
        self.as_setAnomaliesMatrixHotkeyS(_getAnomaliesMatrixHotkey())
        CM.g_instance.onMappingChanged += self.__onMappingChanged
        return

    def _dispose(self):
        VehicleRespawnComponent.onVehicleRespawned -= self._onVehicleRespawned
        vehicleStateCtrl = self.sessionProvider.shared.vehicleState
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart -= self.__onReplayTimeWarpStart
        self.__attentionEffect.destroy()
        self.__attentionEffect = None
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onUpgradeOptionsUpdated -= self.__updateUpgrades
            hwBattleGuiCtrl.onChangeAnomaliesViewVisibility -= self.__onChangeAnomaliesViewVisibility
            hwBattleGuiCtrl.onSelectAnomaly -= self.__onSelectAnomaly
        InputHandler.g_instance.onKeyDown -= self.__handleKeyEvent
        CM.g_instance.onMappingChanged -= self.__onMappingChanged
        self.__callbackDelayer.destroy()
        super(HWBattleUpgradePanel, self)._dispose()
        return

    def _canBeShown(self):
        return self.hwBattleGuiCtrl.isAnomaliesViewVisible or avatar_getter.isVehicleAlive()

    def _onVehicleRespawned(self, vehicle):
        if vehicle.id != BigWorld.player().playerVehicleID:
            return
        self.__updateVisibility(self._canBeShown() and bool(self.upgradeOptions))

    def __playEffect(self, state):
        if self.__localVisible:
            self.__attentionEffect.setVisible(state)

    def __onReplayTimeWarpStart(self):
        if self.__localVisible:
            self.as_setVisibleS(False)
            self.__localVisible = False

    def __updateVisibility(self, isVisible):
        if self.__localVisible != isVisible:
            self.as_setVisibleS(isVisible)
            self.__attentionEffect.setVisible(isVisible)
        self.__localVisible = isVisible

    def __onVehicleStateUpdated(self, stateID, _):
        if not self.upgradeOptions:
            return
        if stateID == VEHICLE_VIEW_STATE.DESTROYED:
            self.__updateVisibility(self._canBeShown())

    def __onLockCooldownFinish(self):
        self.__toggleAlertState(False, '', REASON_EMPTY)
        self.__playEffect(False)
        self.__lockReason = REASON_EMPTY

    def __onChangeAnomaliesViewVisibility(self, isVisible):
        if isVisible:
            hasUpgradeOptions = bool(self.upgradeOptions)
            if hasUpgradeOptions:
                self.__onLockCooldownFinish()
            self.as_setVisibleS(hasUpgradeOptions)
            self.__localVisible = hasUpgradeOptions

    def __onSelectAnomaly(self, anomalyIdx):
        if self.upgradeOptions:
            self.as_showSelectAnimS(anomalyIdx)

    def __toggleAlertState(self, isLocked, text, reasonID):
        self.as_toggleAlertStateS(isLocked, text)

    def __updateUpgrades(self, upgrades):
        self.__callbackDelayer.clearCallbacks()
        if not upgrades:
            self.__updateVisibility(False)
            return
        if len(upgrades) != 2:
            logger.warning('Unexpected modules count. Items list: %s', str(upgrades))
            return
        if self.hwBattleGuiCtrl.isAnomaliesViewVisible:
            self.__onLockCooldownFinish()
        visible = bool(avatar_getter.isVehicleAlive())
        self.__updateVisibility(visible)
        data = {'firstItem': self.__getItemInfo(0),
         'secondItem': self.__getItemInfo(1),
         'title': backport.text(self.TEXT_PATH_PANEL_INFO.title.default())}
        if not self.__textInited:
            data['isInitData'] = True
            self.__textInited = True
        self.as_setDataS(data)

    def __onMappingChanged(self, *_):
        self.as_setAnomaliesMatrixHotkeyS(_getAnomaliesMatrixHotkey())

    def __getItemInfo(self, index):
        anomalyID = self.upgradeOptions[index]
        anomalyData = self.hwAnomaliesCtrl.getAnomalyByID(anomalyID)
        isAnomalyEpic = anomalyData.type == self._EPIC_ANOMALY_TYPE
        itemInfo = {'header': anomalyTitle(anomalyID, isAnomalyEpic),
         'isCombo': isAnomalyInCombo(anomalyID),
         'isNew': isAnomalyNew(anomalyID),
         'parameters': anomalyDescriptionList(anomalyID, lambda v: {'description': v}, isAnomalyEpic),
         'module': {'icon': backport.image(ICONS_PATH.dyn(anomalyID)()),
                    'available': True}}
        if not self.__textInited:
            itemInfo['hotKeys'] = self.__keyInfoList[index]
        return itemInfo

    def __getHotKeyString(self, command):
        return ' +'.join(getHotKeyList(command))

    def __getBattlePage(self):
        app = self.appLoader.getDefBattleApp()
        return app.containerManager.getContainer(WindowLayer.VIEW).getView() if app and app.containerManager else None

    def __handleKeyEvent(self, event):
        page = self.__getBattlePage()
        if not page or not page.as_isComponentVisibleS(self.getAlias()):
            return False
        elif not self.__localVisible:
            return False
        elif self.__lockReason != REASON_EMPTY:
            return
        elif not event.isKeyDown:
            return False
        idx = next((i for i, cmd in enumerate(_KEYS_INFO) if CM.g_instance.isFiredList(cmd, event.key)), None)
        if idx is not None:
            selectAnomaly(idx)
            return True
        else:
            return False

    def __makeHtmlFormat(self, text, format):
        return makeHtmlString('html_templates:battle/textStyle', format, {'text': text})
