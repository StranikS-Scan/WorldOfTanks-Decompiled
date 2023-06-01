# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/battle_upgrade_panel.py
import logging
import weakref
import BigWorld
from ReplayEvents import g_replayEvents
from battle_royale.gui.battle_control.controllers.notification_manager import INotificationManagerListener
from gui.battle_control import avatar_getter
from helpers import dependency
import BattleReplay
import CommandMapping
from gui.Scaleform.daapi.view.common.battle_royale import br_helpers
from gui.Scaleform.daapi.view.common.battle_royale.params import getShortListParameters
from gui.Scaleform.daapi.view.meta.BattleUpgradePanelMeta import BattleUpgradePanelMeta
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from battle_royale.gui.battle_control.controllers.progression_ctrl import IProgressionListener
from gui.doc_loaders.battle_royale_settings_loader import getTreeModuleIcon, getTreeModuleHeader, getBattleRoyaleSettings
from battle_royale.gui.battle_control.controllers.br_battle_sounds import BREvents
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import isItemVehicleHull
from skeletons.gui.battle_session import IBattleSessionProvider
logger = logging.getLogger(__name__)

class _AttentionEffectPlayer(object):
    __slots__ = ('__viewRef', '__callbackID', '__delayTime', '__isPlaying')

    def __init__(self, viewRef):
        super(_AttentionEffectPlayer, self).__init__()
        self.__viewRef = viewRef
        self.__callbackID = None
        self.__delayTime = getBattleRoyaleSettings().upgradeAttentionTime
        self.__isPlaying = False
        return

    def setVisible(self, visible):
        eventName = BREvents.UPGRADE_PANEL_SHOW if visible else BREvents.UPGRADE_PANEL_HIDE
        BREvents.playSound(eventName)
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


class BattleUpgradePanel(BattleUpgradePanelMeta, IArenaVehiclesController, IProgressionListener, INotificationManagerListener):
    __slots__ = ('__level', '__upgrades', '__localVisible', '__isEnabled', '__attentionEffect', 'notificationManager')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleUpgradePanel, self).__init__()
        self.__attentionEffect = _AttentionEffectPlayer(self)
        self.__level = 0
        self.__upgrades = []
        self.__localVisible = False
        self.__isEnabled = True
        self.__textInited = False
        self.notificationManager = None
        return

    def onSelectItem(self, itemID):
        if self.__sessionProvider.isReplayPlaying:
            return
        if self.__upgrades and itemID in self.__upgrades:
            self.as_showSelectAnimS(self.__upgrades.index(itemID))
        self._selectVehicleItem(itemID)

    def updateData(self, arenaLevelData):
        self.__level = arenaLevelData.level
        self.__updateUpgrades()

    def setUpgradeDisabled(self, cooldownTime, reason):
        self.__changeEnabled(state=False, reason=reason)

    def setUpgradeEnabled(self):
        self.__changeEnabled(state=True)

    def setVehicleChanged(self, vehicle, newModuleIntCD, vehicleRecreated):
        if BattleReplay.g_replayCtrl.isPlaying and newModuleIntCD:
            self.as_showSelectAnimS(self.__upgrades.index(newModuleIntCD))
        self.__updateUpgrades()

    def setVehicleChangeResponse(self, itemCD, success):
        if success:
            progressionCtrl = self.__getProgressionCtrl()
            item = progressionCtrl.getModule(itemCD)
            if isItemVehicleHull(itemCD, self._getVehicle()):
                moduleKey = R.strings.battle_royale.player_messages.moduleType.hull
            else:
                moduleKey = R.strings.battle_royale.player_messages.moduleType.dyn(item.itemTypeName, None)
            self.__sessionProvider.shared.messages.onShowPlayerMessageByKey('VEHICLE_UPGRADE', {'module': getTreeModuleHeader(item),
             'moduleType': backport.text(moduleKey()) if moduleKey else ''})
            self.__playEffect(True)
        return

    def addNotificationManager(self, notificationManager):
        self.notificationManager = weakref.ref(notificationManager)
        self.notificationManager().addUpgradePanelHandler(self.__updateUpgrades)

    def selectVehicleModule(self, index):
        if index < len(self.__upgrades):
            self.as_showSelectAnimS(index)
            self._selectVehicleItem(self.__upgrades[index])

    def _populate(self):
        super(BattleUpgradePanel, self)._populate()
        self.__sessionProvider.addArenaCtrl(self)
        vehicleStateCtrl = self.__getVehicleStateCtrl()
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vehicleStateCtrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart += self.__onReplayTimeWarpStart
        return

    def _dispose(self):
        vehicleStateCtrl = self.__getVehicleStateCtrl()
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            vehicleStateCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart -= self.__onReplayTimeWarpStart
        self.__sessionProvider.removeArenaCtrl(self)
        self.__attentionEffect.destroy()
        self.__attentionEffect = None
        self.notificationManager = None
        super(BattleUpgradePanel, self)._dispose()
        return

    def _getVehicle(self):
        return self.__getProgressionCtrl().getCurrentVehicle()

    def _selectVehicleItem(self, itemID):
        progressionCtrl = self.__getProgressionCtrl()
        item = progressionCtrl.getModule(itemID)
        progressionCtrl.vehicleUpgradeRequest(moduleItem=item)

    def _setVisible(self, isVisible):
        self.__localVisible = isVisible

    def __onReplayTimeWarpStart(self):
        if self.__localVisible:
            self.as_setVisibleS(False)
            self.__localVisible = False

    def __updateVisibility(self, isVisible, addToManager=True):
        if addToManager and self.notificationManager():
            self.notificationManager().setUpgradeVisibility(isVisible)
            return
        if self.__localVisible != isVisible:
            self.__attentionEffect.setVisible(isVisible)
            self.as_setVisibleS(isVisible)
        self.__localVisible = isVisible

    def __changeEnabled(self, state, reason=None):
        if reason is not None:
            text = backport.text(R.strings.battle_royale.upgradePanel.alert.num(reason)())
        else:
            text = None
        self.as_toggleAlertStateS(not state, text)
        if self.__isEnabled != state:
            self.__playEffect(state)
        self.__isEnabled = state
        return

    def __onVehicleStateUpdated(self, stateID, _):
        if stateID == VEHICLE_VIEW_STATE.DESTROYED:
            self.__updateUpgrades()

    def __onRespawnBaseMoving(self):
        self.__updateUpgrades()

    def __getVehicleStateCtrl(self):
        return self.__sessionProvider.shared.vehicleState

    def __getUpgradeItems(self):
        battleVehicle = BigWorld.player().getVehicleAttached()
        guiVehicle = self._getVehicle()
        if not guiVehicle or not battleVehicle:
            return
        currentLevel = self.__getCurrentLvl()
        nextVehicleLevel = currentLevel + 1
        upgrades = []
        upgradeCds = []
        if battleVehicle.isAlive() and self.__level > currentLevel:
            progressionCtrl = self.__getProgressionCtrl()
            for _, _, intCD, unlocks in guiVehicle.getUnlocksDescrs():
                if intCD not in upgradeCds:
                    item = self.__getModuleItem(intCD)
                    itemLvl = item.level
                    if itemLvl == nextVehicleLevel and progressionCtrl.mayInstallModule(item):
                        if not br_helpers.isAdditionalModule(itemLvl, unlocks, self.__getModuleItem):
                            upgrades.append(item)
                            upgradeCds.append(intCD)

        return upgrades

    def __updateUpgrades(self, addToManager=True):
        upgrades = self.__getUpgradeItems()
        self.__upgrades = []
        if upgrades:
            hasTwoModules = len(upgrades) == 2
            if hasTwoModules:
                self.__upgrades = [ upgrade.intCD for upgrade in upgrades ]
                first = upgrades[0]
                second = upgrades[1]
                if isItemVehicleHull(first.intCD, self._getVehicle()):
                    titleKey = R.strings.battle_royale.upgradePanel.title.hull
                else:
                    titleKey = R.strings.battle_royale.upgradePanel.title.dyn(first.itemTypeName, None)
                    if titleKey is None:
                        titleKey = R.strings.battle_royale.upgradePanel.title.default
                data = {'firstItem': self.__getModuleInfo(first, 0),
                 'secondItem': self.__getModuleInfo(second, 1),
                 'title': backport.text(titleKey())}
                if not self.__textInited:
                    key = br_helpers.getHotKeyString(CommandMapping.CMD_UPGRADE_PANEL_SHOW)
                    data['description'] = backport.text(R.strings.battle_royale.upgradePanel.description(), key=key)
                    data['isInitData'] = True
                    self.__textInited = True
                self.as_setDataS(data)
                self.__updateVisibility(hasTwoModules and avatar_getter.isVehicleAlive(), addToManager)
            else:
                logger.warning('Unexpected modules count. Modules list: %s', str(upgrades))
        else:
            self.__updateVisibility(False, addToManager)
        return

    def __getModuleInfo(self, moduleItem, index):
        moduleInfo = {'header': getTreeModuleHeader(moduleItem),
         'parameters': getShortListParameters(moduleItem, self._getVehicle()),
         'module': {'icon': getTreeModuleIcon(moduleItem),
                    'intCD': moduleItem.intCD,
                    'available': True}}
        if not self.__textInited:
            moduleInfo['hotKeys'] = br_helpers.getHotKeyListByIndex(index)
            moduleInfo['hotKeysVKeys'] = br_helpers.getHotKeyVkListByIndex(index)
        return moduleInfo

    def __getModuleItem(self, intCD):
        return self.__getProgressionCtrl().getModule(intCD)

    def __playEffect(self, state):
        if self.__localVisible:
            self.__attentionEffect.setVisible(state)

    def __getCurrentLvl(self):
        return self.__getProgressionCtrl().getCurrentVehicleLevel()

    def __getProgressionCtrl(self):
        return self.__sessionProvider.dynamic.progression
