# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/Scaleform/daapi/view/lobby/hangar/armory_yard_vehicle_preview.py
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview, VEHICLE_PREVIEW_ALIASES
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.bonuses import getNonQuestBonuses, VehiclesBonus
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController, IHeroTankController
from web.web_client_api.common import ItemPackEntry, ItemPackType
VEHICLE_PREVIEW_ALIASES.append(HANGAR_ALIASES.ARMORY_YARD_VEHICLE_PREVIEW)

class ArmoryYardVehiclePreview(VehiclePreview):
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __heroTanksControl = dependency.descriptor(IHeroTankController)

    def __init__(self, ctx=None):
        super(ArmoryYardVehiclePreview, self).__init__(ctx)
        self._showHeroTankText = ctx.get('showHeroTankText', False)
        self._heroInteractive = False
        currentHeroTankCD = self.__heroTanksControl.getCurrentTankCD()
        self.__needHeroTankHidden = not ctx.get('isHeroTank', False) and self._vehicleCD == currentHeroTankCD
        self.__backToHeroTank = ctx.get('isHeroTank', False)

    def _populate(self):
        super(ArmoryYardVehiclePreview, self)._populate()
        if self.__needHeroTankHidden:
            self.__heroTanksControl.setHidden(True)

    def _dispose(self):
        if self.__needHeroTankHidden:
            self.__heroTanksControl.setHidden(False)
        super(ArmoryYardVehiclePreview, self)._dispose()

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
