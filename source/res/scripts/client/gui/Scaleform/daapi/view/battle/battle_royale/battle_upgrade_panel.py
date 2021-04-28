# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/battle_upgrade_panel.py
import logging
from ReplayEvents import g_replayEvents
from gui.battle_control import avatar_getter
from helpers import dependency
import BattleReplay
import CommandMapping
from gui.Scaleform.daapi.view.battle.shared.attention_effect_player import AttentionEffectPlayer
from gui.Scaleform.daapi.view.common.battle_royale import br_helpers
from gui.Scaleform.daapi.view.common.battle_royale.params import getShortListParameters
from gui.Scaleform.daapi.view.meta.BattleUpgradePanelMeta import BattleUpgradePanelMeta
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.controllers.progression_ctrl import IProgressionListener
from gui.doc_loaders.battle_royale_settings_loader import getTreeModuleIcon, getTreeModuleHeader, getBattleRoyaleSettings
from gui.game_control.br_battle_sounds import BREvents
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import isItemVehicleHull
from skeletons.gui.battle_session import IBattleSessionProvider
logger = logging.getLogger(__name__)

class _UpgradePanelAttentionPlayer(AttentionEffectPlayer):
    __slots__ = ()

    def setVisible(self, visible):
        eventName = BREvents.UPGRADE_PANEL_SHOW if visible else BREvents.UPGRADE_PANEL_HIDE
        BREvents.playSound(eventName)
        super(_UpgradePanelAttentionPlayer, self).setVisible(visible)

    def _setDelayTime(self):
        return getBattleRoyaleSettings().upgradeAttentionTime


class BattleUpgradePanel(BattleUpgradePanelMeta, IArenaVehiclesController, IProgressionListener):
    __slots__ = ('__level', '__upgrades', '__localVisible', '__isEnabled', '__attentionEffect')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleUpgradePanel, self).__init__()
        self.__attentionEffect = _UpgradePanelAttentionPlayer(self)
        self.__level = 0
        self.__upgrades = []
        self.__localVisible = False
        self.__isEnabled = True
        self.__textInited = False

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

    def selectVehicleModule(self, index):
        if index < len(self.__upgrades):
            self.as_showSelectAnimS(index)
            self._selectVehicleItem(self.__upgrades[index])

    def showNotificationAnim(self):
        self.as_showNotificationAnimS()

    def hideNotificationAnim(self):
        self.as_hideNotificationAnimS()

    def _populate(self):
        super(BattleUpgradePanel, self)._populate()
        self.__sessionProvider.addArenaCtrl(self)
        vehicleStateCtrl = self.__getVehicleStateCtrl()
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart += self.__onReplayTimeWarpStart
        return

    def _dispose(self):
        vehicleStateCtrl = self.__getVehicleStateCtrl()
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart -= self.__onReplayTimeWarpStart
        self.__sessionProvider.removeArenaCtrl(self)
        self.__attentionEffect.destroy()
        self.__attentionEffect = None
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

    def __updateVisibility(self, isVisible):
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
        if stateID == VEHICLE_VIEW_STATE.DEATH_INFO:
            self.__upgrades = []
            self.__updateVisibility(False)

    def __getVehicleStateCtrl(self):
        return self.__sessionProvider.shared.vehicleState

    def __getUpgradeItems(self):
        vehicle = self._getVehicle()
        if not vehicle:
            return
        currentLevel = self.__getCurrentLvl()
        nextVehicleLevel = currentLevel + 1
        upgrades = []
        upgradeCds = []
        if vehicle.isAlive and self.__level > currentLevel:
            progressionCtrl = self.__getProgressionCtrl()
            for _, _, intCD, unlocks in vehicle.getUnlocksDescrs():
                if intCD not in upgradeCds:
                    item = self.__getModuleItem(intCD)
                    itemLvl = item.level
                    if itemLvl == nextVehicleLevel and progressionCtrl.mayInstallModule(item):
                        if not br_helpers.isAdditionalModule(itemLvl, unlocks, self.__getModuleItem):
                            upgrades.append(item)
                            upgradeCds.append(intCD)

        return upgrades

    def __updateUpgrades(self):
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
                self.__updateVisibility(hasTwoModules and avatar_getter.isVehicleAlive())
            else:
                logger.warning('Unexpected modules count. Modules list: %s', str(upgrades))
        else:
            self.__updateVisibility(False)
        return

    def __getModuleInfo(self, moduleItem, index):
        moduleInfo = {'header': getTreeModuleHeader(moduleItem),
         'parameters': getShortListParameters(moduleItem, self._getVehicle()),
         'module': {'icon': getTreeModuleIcon(moduleItem),
                    'intCD': moduleItem.intCD,
                    'available': True}}
        if not self.__textInited:
            moduleInfo['hotKeys'] = br_helpers.getHotKeyListByIndex(index)
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
