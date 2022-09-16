# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/veh_configurator.py
import logging
import GUI
from adisp import adisp_process
from gui.Scaleform.daapi.view.common.battle_royale import br_helpers
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from helpers import dependency
import BattleReplay
from ReplayEvents import g_replayEvents
from gui.Scaleform.daapi.view.common.battle_royale.params import getShortListParameters
from gui.Scaleform.daapi.view.common.battle_royale.br_helpers import getHotKeyListByIndex
from battle_royale.gui.Scaleform.daapi.view.common.veh_modules_config_cmp import VehicleModulesConfiguratorCmp
from gui.Scaleform.daapi.view.meta.BattleVehicleConfiguratorMeta import BattleVehicleConfiguratorMeta
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from battle_royale.gui.battle_control.controllers.progression_ctrl import IProgressionListener, createGuiVehicle
from gui.doc_loaders.battle_royale_settings_loader import getTreeModuleHeader, getTreeModuleIcon
from battle_royale.gui.battle_control.controllers.br_battle_sounds import BREvents
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from items import parseIntCompactDescr
from gui.shared.gui_items.processors.module import getPreviewInstallerProcessor
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.shared.gui_items import IGuiItemsFactory
_logger = logging.getLogger(__name__)

class BattleVehicleConfiguratorCmp(VehicleModulesConfiguratorCmp, IProgressionListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleVehicleConfiguratorCmp, self).__init__()
        self.__moduleChangeCallback = None
        return

    def setVehicleChanged(self, vehicle, newModuleIntCD, vehicleRecreated):
        if vehicleRecreated:
            self.setVehicle(vehicle)
            self._recreate()
        elif newModuleIntCD is not None:
            self.setVehicle(vehicle)
            self._syncVehicle(newModuleIntCD)
        else:
            _logger.error('Invalid data has been received! New module id can not be "%s"!', newModuleIntCD)
        return

    def setVehicle(self, vehicle):
        super(BattleVehicleConfiguratorCmp, self).setVehicle(createGuiVehicle(vehicle.descriptor.makeCompactDescr()))

    def updateData(self, arenaLevelData):
        self.setAvailableLevel(arenaLevelData.level)

    def setModuleChangeCallback(self, callback):
        self.__moduleChangeCallback = callback

    def as_setItemsS(self, items):
        super(BattleVehicleConfiguratorCmp, self).as_setItemsS(items)
        self.__sendHighlightedModulesUpdate()

    def as_updateItemsS(self, items):
        super(BattleVehicleConfiguratorCmp, self).as_updateItemsS(items)
        self.__sendHighlightedModulesUpdate()

    def onClick(self, intCD, columnIdx, moduleIdx):
        if self.__sessionProvider.isReplayPlaying:
            return
        intCD = int(intCD)
        columnIdx = int(columnIdx)
        moduleIdx = int(moduleIdx)
        module = self._getItem(intCD)
        success = self._mayInstallModuleOnCurrentVehicle(module)
        if success:
            self.__installModuleOnLocalVehicle(module)
            column = self._columnsVOs[columnIdx]
            updatedIndexes = set()
            moduleVO = column['modules'][moduleIdx]
            if not moduleVO['selected']:
                moduleVO['selected'] = True
                column['selected'] = True
                for prevModule in self._columnsVOs[columnIdx - 1]['modules']:
                    if prevModule['selected']:
                        moduleVO['activeLink'] = prevModule['intCD']
                        break

                module = self._getItem(intCD)
                self._setCurrentLevel(module.level)
                updatedIndexes.add(columnIdx)
                self._sendUpdate(updatedIndexes | self._updateColumns())
                self.__getProgressionCtrl().vehicleUpgradeRequest(intCD)
        else:
            _logger.warning('Attempt to select unsuitable module %s !', intCD)

    def _dispose(self):
        self.__moduleChangeCallback = None
        super(BattleVehicleConfiguratorCmp, self)._dispose()
        return

    def _mayInstallModuleOnCurrentVehicle(self, mItem):
        return self.__getProgressionCtrl().mayInstallModuleOnVehicle(mItem, self._vehicle)

    def _installModule(self, moduleItem):
        return self.__getProgressionCtrl().vehicleUpgradeRequest(moduleItem=moduleItem)

    def _canBeShown(self, intCD, level, unlocks):
        return not br_helpers.isAdditionalModule(level, unlocks, self._getItem)

    def _isModuleSelected(self, item, vehicle):
        selected = super(BattleVehicleConfiguratorCmp, self)._isModuleSelected(item, vehicle)
        if not selected:
            selected = self.__getProgressionCtrl().isModuleSelected(item.intCD)
        return selected

    def _getItem(self, intCD):
        return self.__getProgressionCtrl().getModule(intCD)

    def __sendHighlightedModulesUpdate(self):
        if self.__moduleChangeCallback:
            self.__moduleChangeCallback(self._getHighlightedModules())

    def __getProgressionCtrl(self):
        return self.__sessionProvider.dynamic.progression

    @adisp_process
    def __installModuleOnLocalVehicle(self, module):
        yield getPreviewInstallerProcessor(self._vehicle, module).request()


class BattleVehicleConfigurator(BattleVehicleConfiguratorMeta, IProgressionListener, BattleGUIKeyHandler):
    __slots__ = ('__cmpAliases', '__configuratorCmp', '__blur', '__isActive')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)
    _MAX_SELECTED_HIGHLIGHTED_MODULES = 2

    def __init__(self, *args, **kwargs):
        super(BattleVehicleConfigurator, self).__init__(*args, **kwargs)
        self.__cmpAliases = {BATTLE_VIEW_ALIASES.BATTLE_VEH_MODULES_CONFIGURATOR_CMP, BATTLE_VIEW_ALIASES.BATTLE_LEVEL_PANEL}
        self.__configuratorCmp = None
        self.__blur = GUI.WGUIBackgroundBlur()
        self.__isActive = False
        return

    def updateData(self, arenaLevelData):
        for cmpnt in self.components.values():
            cmpnt.updateData(arenaLevelData)

    def setVehicleChanged(self, vehicle, moduleIntCD, vehicleRecreated):
        for cmpnt in self.components.values():
            cmpnt.setVehicleChanged(vehicle, moduleIntCD, vehicleRecreated)

    def onMaxLvlAchieved(self):
        for cmpnt in self.components.values():
            cmpnt.onMaxLvlAchieved()

    def setUpgradeDisabled(self, *args):
        self.destroy()

    def handleEscKey(self, isDown):
        if isDown:
            self.destroy()
        return isDown

    def _populate(self):
        super(BattleVehicleConfigurator, self)._populate()
        if self.app is not None:
            self.app.registerGuiKeyHandler(self)
        self.addListener(GameEvent.HIDE_VEHICLE_UPGRADE, self.__handleHide, EVENT_BUS_SCOPE.BATTLE)
        self.__blur.enable = True
        vehicle = self.__getProgressionVehicle()
        self.as_setDataS({'vehTypeIcon': getTypeBigIconPath(vehicle.type),
         'vehName': vehicle.userName})
        vehicleStateCtrl = self.__getVehicleStateCtrl()
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart += self.__onReplayTimeWarpStart
        BREvents.playSound(BREvents.VEH_CONFIGURATOR_SHOW)
        self.__isActive = True
        return

    def onModuleMouseOver(self, intCD):
        vo = self.__getModuleInfoPanel(intCD)
        if vo is not None:
            self.as_updateModuleInfoPanelS(vo)
        return

    def _dispose(self):
        vehicleStateCtrl = self.__getVehicleStateCtrl()
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart -= self.__onReplayTimeWarpStart
        self.__configuratorCmp = None
        ctrl = self.__getProgressionCtrl()
        if ctrl is not None:
            ctrl.removeRuntimeView(self)
        if self.app is not None:
            self.app.unregisterGuiKeyHandler(self)
        self.removeListener(GameEvent.HIDE_VEHICLE_UPGRADE, self.__handleHide, EVENT_BUS_SCOPE.BATTLE)
        self.__blur.enable = False
        self.__isActive = False
        BREvents.playSound(BREvents.VEH_CONFIGURATOR_HIDE)
        super(BattleVehicleConfigurator, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(BattleVehicleConfigurator, self)._onRegisterFlashComponent(viewPy, alias)
        if alias in self.__cmpAliases:
            if isinstance(viewPy, BattleVehicleConfiguratorCmp):
                viewPy.setModuleChangeCallback(self.__onComponentModulesChanged)
                viewPy.setVehicle(self.__getProgressionVehicle())
                self.__configuratorCmp = viewPy
            self.__cmpAliases.remove(alias)
            if not self.__cmpAliases:
                self.__getProgressionCtrl().addRuntimeView(self)

    def __onReplayTimeWarpStart(self):
        if self.__isActive:
            self.destroy()

    def __onVehicleStateUpdated(self, stateID, _):
        if stateID == VEHICLE_VIEW_STATE.DEATH_INFO:
            self.destroy()

    def __getProgressionCtrl(self):
        return self.sessionProvider.dynamic.progression

    def __getVehicleStateCtrl(self):
        return self.sessionProvider.shared.vehicleState

    def __onComponentModulesChanged(self, modules):
        modulesCount = len(modules)
        if modulesCount == self._MAX_SELECTED_HIGHLIGHTED_MODULES:
            self.as_updateChoiceInfoPanelS({'firstItem': self.__getModuleInfo(*modules[0]),
             'secondItem': self.__getModuleInfo(*modules[1])})
        elif modulesCount != 0:
            _logger.warning('%s or None modules can be highlighted. Received list instead: %s', str(self._MAX_SELECTED_HIGHLIGHTED_MODULES), str(modules))

    def __getModuleInfo(self, intCD, icon, index):
        module = self.__getModuleItem(intCD)
        return {'header': getTreeModuleHeader(module),
         'parameters': getShortListParameters(module, self.__getProgressionVehicle(), self.__getInstalledOnVehicleAnalogByIntCD(intCD)),
         'hotKeysVKeys': getHotKeyListByIndex(index),
         'hotKeys': getHotKeyListByIndex(index),
         'module': {'icon': icon,
                    'intCD': intCD,
                    'available': True}}

    def __getModuleInfoPanel(self, intCD):
        itemTypeID, _, _ = parseIntCompactDescr(intCD)
        if itemTypeID != GUI_ITEM_TYPE.VEHICLE:
            module = self.__getModuleItem(intCD)
            if module is not None:
                return {'header': getTreeModuleHeader(module),
                 'parameters': getShortListParameters(module, self.__getProgressionVehicle(), self.__getInstalledOnVehicleAnalogByIntCD(intCD)),
                 'module': {'icon': getTreeModuleIcon(module),
                            'available': True}}
        return

    def __getModuleItem(self, intCD):
        return self.__getProgressionCtrl().getModule(intCD)

    def __getInstalledOnVehicleAnalogByIntCD(self, intCD):
        return self.__getProgressionCtrl().getInstalledOnVehicleAnalogByIntCD(intCD)

    def __getProgressionVehicle(self):
        return self.__getProgressionCtrl().getCurrentVehicle()

    def __handleHide(self, _):
        self.destroy()
