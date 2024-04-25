# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/Scaleform/daapi/view/lobby/hangar/armory_yard_vehicle_preview.py
from armory_yard.gui.Scaleform.daapi.view.lobby.hangar.sound_constants import ARMORY_YARD_VEHICLE_PREVIEW_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview, VEHICLE_PREVIEW_ALIASES
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.listener import IGlobalListener
from gui.server_events.bonuses import getNonQuestBonuses, VehiclesBonus
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showHangar
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController, IHeroTankController
from web.web_client_api.common import ItemPackEntry, ItemPackType
VEHICLE_PREVIEW_ALIASES.append(HANGAR_ALIASES.ARMORY_YARD_VEHICLE_PREVIEW)

class ArmoryYardVehiclePreview(VehiclePreview, IGlobalListener):
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __heroTanksControl = dependency.descriptor(IHeroTankController)
    _COMMON_SOUND_SPACE = ARMORY_YARD_VEHICLE_PREVIEW_SOUND_SPACE

    def __init__(self, ctx=None):
        super(ArmoryYardVehiclePreview, self).__init__(ctx)
        self._showHeroTankText = ctx.get('showHeroTankText', False)
        self._heroInteractive = False
        currentHeroTankCD = self.__heroTanksControl.getCurrentTankCD()
        self.__needHeroTankHidden = not ctx.get('isHeroTank', False) and self._vehicleCD == currentHeroTankCD
        self.__backToHeroTank = ctx.get('isHeroTank', False)

    def onPrbEntitySwitching(self):
        self.__armoryYardCtrl.unloadScene(isReload=False)
        self.closeView()
        showHangar()

    def _getData(self):
        result = super(ArmoryYardVehiclePreview, self)._getData()
        result['showCloseBtn'] = False
        return result

    def _populate(self):
        super(ArmoryYardVehiclePreview, self)._populate()
        if self.__needHeroTankHidden:
            self.__heroTanksControl.setHidden(True)
        self.__updateVisibilityHangarHeaderMenu()
        self.startGlobalListening()

    def _dispose(self):
        if self.__needHeroTankHidden:
            self.__heroTanksControl.setHidden(False)
        self.__updateVisibilityHangarHeaderMenu(isVisible=True)
        self.stopGlobalListening()
        super(ArmoryYardVehiclePreview, self)._dispose()
        if self.__armoryYardCtrl.isVehiclePreview:
            self.__armoryYardCtrl.unloadScene()

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_PY_ALIAS and self._showHeroTankText:
            viewPy.setPanelTextData(backport.text(R.strings.armory_yard.prevView.title()), backport.text(R.strings.armory_yard.prevView.button()), text_styles.highTitleRegular(backport.text(R.strings.armory_yard.prevView.body())))
        elif alias == VEHPREVIEW_CONSTANTS.CREW_LINKAGE:
            stepsRewards = self.__armoryYardCtrl.getStepsRewards()
            stepCount = self.__armoryYardCtrl.getTotalSteps()
            finalVehicleReward = stepsRewards.get(stepCount, {}).get('vehicles', {})
            finalVehicleBonus = getNonQuestBonuses(VehiclesBonus.VEHICLES_BONUS, finalVehicleReward)[0]
            vehicle = [VehiclesBonus.wrapToItemsPack(finalVehicleBonus)[0]]
            crew = [ItemPackEntry(id=1, type=ItemPackType.CREW_100, count=1, groupID=1)]
            viewPy.setVehicleCrews(vehicle, crew)

    def _getExitEvent(self):
        exitEvent = super(ArmoryYardVehiclePreview, self)._getExitEvent()
        exitEvent.ctx.update({'showHeroTankText': self._showHeroTankText,
         'backToHeroTank': self.__backToHeroTank})
        return exitEvent

    def closeView(self):
        self.destroy()

    def __updateVisibilityHangarHeaderMenu(self, isVisible=False):
        state = HeaderMenuVisibilityState.NOTHING if not isVisible else HeaderMenuVisibilityState.ALL
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': state}), EVENT_BUS_SCOPE.LOBBY)
