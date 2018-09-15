# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/ranked/carousel_data_provider.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.functions import makeTooltip

class RankedCarouselDataProvider(HangarCarouselDataProvider):

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        result = [vehicle.getCustomState() == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE]
        result.extend(super(RankedCarouselDataProvider, cls)._vehicleComparisonKey(vehicle))
        return result

    def _buildVehicle(self, vehicle):
        result = super(RankedCarouselDataProvider, self)._buildVehicle(vehicle)
        vehRank, _ = self._itemsCache.items.ranked.vehRanks.get(vehicle.intCD, (0, 0))
        if vehRank > 0:
            result['vehRankVisible'] = True
            if vehRank > 1:
                result['vehRankLabel'] = text_styles.counterLabelText(vehRank)
        state, _ = vehicle.getState()
        if state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE:
            result['lockedTooltip'] = makeTooltip(RANKED_BATTLES.RANKEDBATTLESCAROUSEL_LOCKEDTOOLTIP_HEADER, RANKED_BATTLES.RANKEDBATTLESCAROUSEL_LOCKEDTOOLTIP_BODY)
        return result
