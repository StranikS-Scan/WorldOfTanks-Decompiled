# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/ranked/carousel_data_provider.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.functions import makeTooltip
from gui.ranked_battles.constants import RANK_TYPES
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedCarouselDataProvider(HangarCarouselDataProvider):
    rankedController = dependency.descriptor(IRankedBattlesController)

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        result = [vehicle.getCustomState() == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE]
        result.extend(super(RankedCarouselDataProvider, cls)._vehicleComparisonKey(vehicle))
        return result

    def _buildVehicle(self, vehicle):
        result = super(RankedCarouselDataProvider, self)._buildVehicle(vehicle)
        rank = self.rankedController.getCurrentRank(vehicle)
        if rank.getType() == RANK_TYPES.VEHICLE:
            result['vehRankVisible'] = True
            rankId = rank.getSerialID()
            if rankId > 1:
                result['vehRankLabel'] = text_styles.counterLabelText(rankId)
        state, _ = vehicle.getState()
        if state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE:
            result['lockedTooltip'] = makeTooltip(RANKED_BATTLES.RANKEDBATTLESCAROUSEL_LOCKEDTOOLTIP_HEADER, RANKED_BATTLES.RANKEDBATTLESCAROUSEL_LOCKEDTOOLTIP_BODY)
        return result
