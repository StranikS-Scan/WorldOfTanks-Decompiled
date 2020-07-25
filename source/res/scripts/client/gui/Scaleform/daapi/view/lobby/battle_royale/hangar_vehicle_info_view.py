# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/hangar_vehicle_info_view.py
import logging
import CommandMapping
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import AccountSettings, BATTLE_ROYALE_HANGAR_BOTTOM_PANEL_VIEWED
from frameworks.wulf import ViewFlags, WindowFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.common.battle_royale import br_helpers
from gui.Scaleform.daapi.view.common.veh_modules_config_cmp import VehicleModulesConfiguratorCmp, getVehicleNationIcon
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_sounds import BATTLE_ROYALE_VEHICLE_INFO_SOUND_SPACE
from gui.Scaleform.daapi.view.meta.BattleRoyaleVehicleInfoMeta import BattleRoyaleVehicleInfoMeta
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.vehicle_info_intro_overlay_model import VehicleInfoIntroOverlayModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items import Vehicle
from gui.shared.utils.functions import makeTooltip
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.shared import IItemsCache
from gui.prb_control.entities.listener import IGlobalListener
_logger = logging.getLogger(__name__)

def _getTabData():
    return ({'viewId': BATTLEROYALE_ALIASES.VEH_MODULES_CONFIGURATOR_CMP,
      'label': backport.text(R.strings.battle_royale.hangarVehicleInfo.moduleTreeTab()),
      'linkage': 'VehModuleConfiguratorCmpUI',
      'selected': True,
      'enabled': True,
      'tipText': text_styles.highlightText(backport.text(R.strings.battle_royale.hangarVehicleInfo.moduleTreeTip(), key=text_styles.neutral(br_helpers.getHotKeyString(CommandMapping.CMD_UPGRADE_PANEL_SHOW)))),
      'tooltipComplexStr': None,
      'tooltipSpecialId': TOOLTIPS_CONSTANTS.BATTLE_ROYALE_BATTLE_PROGRESSION}, {'viewId': BATTLEROYALE_ALIASES.VEHICLE_WEAK_ZONES_CMP,
      'label': backport.text(R.strings.battle_royale.hangarVehicleInfo.weakZonesTab()),
      'linkage': 'VehicleWeakZonesCmpUI',
      'selected': False,
      'enabled': True,
      'tipText': text_styles.highlightText(backport.text(R.strings.battle_royale.hangarVehicleInfo.weakZonesTip())),
      'tooltipComplexStr': makeTooltip(header=backport.text(R.strings.battle_royale.hangarVehicleInfo.tooltips.weakZones.header()), body=backport.text(R.strings.battle_royale.hangarVehicleInfo.tooltips.weakZones.body())),
      'tooltipSpecialId': None})


def _getVehicleWeakZonesImage(vehicle):
    vehicleName = Vehicle.getIconResourceName(vehicle.name)
    dynResource = R.images.gui.maps.icons.battleRoyale.weakZones.dyn(vehicleName)
    if not dynResource.exists():
        _logger.error("Couldn't find weak zones image source for vehicle: %s", vehicleName)
        return ''
    return backport.image(dynResource())


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


class _HangarVehicleInfoIntroView(ViewImpl):
    __slots__ = ('__vehicle', '__firstView', '__blur')

    def __init__(self, layoutID, ctx=None, *args, **kwargs):
        super(_HangarVehicleInfoIntroView, self).__init__(layoutID, ViewFlags.OVERLAY_VIEW, VehicleInfoIntroOverlayModel, *args, **kwargs)
        self.__vehicle = ctx.get('vehicle')
        self.__firstView = ctx.get('firstView', False)
        self.__blur = CachedBlur(enabled=True, ownLayer=APP_CONTAINERS_NAMES.OVERLAY, layers=[APP_CONTAINERS_NAMES.VIEWS,
         APP_CONTAINERS_NAMES.SUBVIEW,
         APP_CONTAINERS_NAMES.TOP_SUB_VIEW,
         APP_CONTAINERS_NAMES.WINDOWS,
         APP_CONTAINERS_NAMES.BROWSER,
         APP_CONTAINERS_NAMES.DIALOGS])

    def _initialize(self):
        super(_HangarVehicleInfoIntroView, self)._initialize()
        with self.getViewModel().transaction() as viewModel:
            viewModel.setVehicleTag(Vehicle.getIconResourceName(self.__vehicle.name))
            viewModel.setIsFirstView(self.__firstView)
            viewModel.onSubmitBtnClick += self.__onSubmitClicked

    def _finalize(self):
        if self.__firstView:
            AccountSettings.setSettings(BATTLE_ROYALE_HANGAR_BOTTOM_PANEL_VIEWED, True)
        self.getViewModel().onSubmitBtnClick -= self.__onSubmitClicked
        self.__vehicle = None
        self.__blur.fini()
        self.__blur = None
        super(_HangarVehicleInfoIntroView, self)._finalize()
        return

    def __onSubmitClicked(self):
        self.destroyWindow()


class _HangarVehicleInfoIntroWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(_HangarVehicleInfoIntroWindow, self).__init__(wndFlags=WindowFlags.OVERLAY, decorator=None, content=_HangarVehicleInfoIntroView(R.views.lobby.battleRoyale.vehicle_info_intro_overlay.VehicleInfoIntroOverlay(), *args, **kwargs))
        return


class HangarVehicleInfo(BattleRoyaleVehicleInfoMeta, IGlobalListener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    _COMMON_SOUND_SPACE = BATTLE_ROYALE_VEHICLE_INFO_SOUND_SPACE

    def __init__(self, ctx=None):
        super(HangarVehicleInfo, self).__init__(ctx)
        self.__guiVehConfigurator = None
        self.__vehicle = self.__itemsCache.items.getItemByCD(g_currentVehicle.item.intCD)
        self.__isFirstEnter = ctx.get('isFirstEnter', False)
        self.__introPage = None
        self.__blur = CachedBlur(enabled=True)
        return

    def getSelectedVehicle(self):
        return self.__vehicle

    def onClose(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def onShowIntro(self):
        self.__showIntroPage()

    def onPrbEntitySwitched(self):
        if not self.__battleRoyaleController.isBattleRoyaleMode():
            self.onClose()

    def _populate(self):
        super(HangarVehicleInfo, self)._populate()
        if self.__isFirstEnter:
            self.__showIntroPage()
            self.__isFirstEnter = False
        self.__battleRoyaleController.onUpdated += self.__onBattleRoyaleEnabledChanged
        self.startGlobalListening()
        self.as_setTabsDataS(_getTabData())
        self.as_setDataS({'btnInfoLabel': backport.text(R.strings.battle_royale.hangarVehicleInfo.infoBtn()),
         'btnCloseLabel': backport.text(R.strings.battle_royale.hangarVehicleInfo.closeBtn()),
         'infoIconSource': backport.image(R.images.gui.maps.icons.library.info()),
         'engineLabel': backport.text(R.strings.battle_royale.hangarVehicleInfo.weakZones.engine()),
         'ammunitionLabel': backport.text(R.strings.battle_royale.hangarVehicleInfo.weakZones.ammunition()),
         'vehTitle': text_styles.promoSubTitle(self.__vehicle.shortUserName),
         'nationIcon': getVehicleNationIcon(self.__vehicle),
         'weakZones': _getVehicleWeakZonesImage(self.__vehicle)})

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

    def __showIntroPage(self):
        self.__introPage = _HangarVehicleInfoIntroWindow(ctx={'vehicle': self.__vehicle,
         'firstView': self.__isFirstEnter})
        self.__introPage.load()

    def __onBattleRoyaleEnabledChanged(self):
        isEnabled = self.__battleRoyaleController.isEnabled()
        if not isEnabled:
            self.onClose()
