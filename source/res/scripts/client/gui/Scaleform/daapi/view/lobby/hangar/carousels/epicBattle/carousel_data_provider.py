# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/epicBattle/carousel_data_provider.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.functions import makeTooltip

class EpicBattleCarouselDataProvider(HangarCarouselDataProvider):

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        result = [vehicle.getCustomState() == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE]
        result.extend(super(EpicBattleCarouselDataProvider, cls)._vehicleComparisonKey(vehicle))
        return result

    def _buildVehicle(self, vehicle):
        result = super(EpicBattleCarouselDataProvider, self)._buildVehicle(vehicle)
        state, _ = vehicle.getState()
        if state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE:
            result['lockedTooltip'] = makeTooltip(EPIC_BATTLE.EPICBATTLESCAROUSEL_LOCKEDTOOLTIP_HEADER, EPIC_BATTLE.EPICBATTLESCAROUSEL_LOCKEDTOOLTIP_BODY)
        result['xpImgSource'] = ''
        return result
