# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/hangar_vehicle_info_view.py
import logging
import CommandMapping
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.battle_royale import br_helpers
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from battle_royale.gui.Scaleform.daapi.view.common.veh_modules_config_cmp import VehicleModulesConfiguratorCmp
from battle_royale_sounds import BATTLE_ROYALE_VEHICLE_INFO_SOUND_SPACE
from gui.Scaleform.daapi.view.meta.BattleRoyaleVehicleInfoMeta import BattleRoyaleVehicleInfoMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.shared import IItemsCache
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import FUNCTIONAL_FLAG
_logger = logging.getLogger(__name__)

class HangarVehicleModulesConfigurator(VehicleModulesConfiguratorCmp):
    __itemsCache = dependency.descriptor(IItemsCache)
    __INITIAL_LEVEL = 2

    def setVehicle(self, vehicle):
        oldVeh = self._vehicle
        super(HangarVehicleModulesConfigurator, self).setVehicle(vehicle)
        if oldVeh is not None:
            self._refresh()
        self.setAvailableLevel(self.__INITIAL_LEVEL)
        return

    def setAvailableLevel(self, level):
        super(HangarVehicleModulesConfigurator, self).setAvailableLevel(self.__INITIAL_LEVEL)

    def getAvailableLevel(self):
        return self.__INITIAL_LEVEL

    def _getItem(self, intCD):
        return self.__itemsCache.items.getItemByCD(intCD)

    def _updateColumns(self):
        columnIdx = 0
        totalColumns = len(self._columnsVOs)
        changedColumns = set()
        while columnIdx < totalColumns:
            columnVo = self._columnsVOs[columnIdx]
            if not columnVo['selected']:
                columnVo['selected'] = False
                changedColumns.add(columnIdx)
            columnIdx += 1

        return changedColumns

    def _syncVehicle(self, intCD):
        pass

    def _recreate(self):
        pass

    def _getHighlightedModules(self):
        return []

    def _isModuleSelected(self, item, vehicle):
        return False

    def _canBeShown(self, intCD, level, unlocks):
        return not br_helpers.isAdditionalModule(level, unlocks, self._getItem)

    def _setCurrentLevel(self, moduleLevel):
        super(HangarVehicleModulesConfigurator, self)._setCurrentLevel(1)


class HangarVehicleInfo(BattleRoyaleVehicleInfoMeta, IGlobalListener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    _COMMON_SOUND_SPACE = BATTLE_ROYALE_VEHICLE_INFO_SOUND_SPACE

    def __init__(self, ctx=None):
        super(HangarVehicleInfo, self).__init__(ctx)
        self.__guiVehConfigurator = None
        self.__vehicle = self.__itemsCache.items.getItemByCD(g_currentVehicle.item.intCD)
        self.__introPage = None
        self.__blur = CachedBlur(enabled=True)
        return

    def getSelectedVehicle(self):
        return self.__vehicle

    def onClose(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def onPrbEntitySwitching(self):
        if self.prbEntity is None:
            return
        else:
            switchedFromBR = bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.BATTLE_ROYALE)
            if switchedFromBR and not self.isDisposed():
                self.onClose()
                self.destroy()
            return

    def onPrbEntitySwitched(self):
        if not self.__battleRoyaleController.isBattleRoyaleMode():
            self.onClose()

    def _populate(self):
        super(HangarVehicleInfo, self)._populate()
        self.__battleRoyaleController.onUpdated += self.__onBattleRoyaleEnabledChanged
        self.startGlobalListening()
        self.as_setDataS({'btnCloseLabel': backport.text(R.strings.battle_royale.hangarVehicleInfo.closeBtn()),
         'infoIconSource': backport.image(R.images.gui.maps.icons.library.info()),
         'infoText': text_styles.highlightText(backport.text(R.strings.battle_royale.hangarVehicleInfo.moduleTreeTip(), key=text_styles.neutral(br_helpers.getHotKeyString(CommandMapping.CMD_UPGRADE_PANEL_SHOW)))),
         'vehTitle': text_styles.grandTitle(self.__vehicle.shortUserName),
         'vehTypeIcon': getTypeBigIconPath(self.__vehicle.type),
         'tutorialText': backport.text(R.strings.battle_royale.hangarVehicleInfo.tutorialText())})

    def _onRegisterFlashComponent(self, viewPy, alias):
        if isinstance(viewPy, HangarVehicleModulesConfigurator):
            viewPy.setVehicle(self.__vehicle)
            self.__guiVehConfigurator = viewPy
        super(HangarVehicleInfo, self)._onRegisterFlashComponent(viewPy, alias)

    def _dispose(self):
        if self.__introPage is not None:
            self.__introPage.destroy()
        self.__battleRoyaleController.onUpdated -= self.__onBattleRoyaleEnabledChanged
        self.stopGlobalListening()
        self.__blur.fini()
        self.__blur = None
        self.__vehicle = None
        self.__guiVehConfigurator = None
        super(HangarVehicleInfo, self)._dispose()
        return

    def __onBattleRoyaleEnabledChanged(self):
        isEnabled = self.__battleRoyaleController.isEnabled()
        if not isEnabled:
            self.onClose()
