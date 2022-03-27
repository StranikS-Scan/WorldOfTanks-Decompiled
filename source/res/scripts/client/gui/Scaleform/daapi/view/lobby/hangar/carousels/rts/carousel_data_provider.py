# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/rts/carousel_data_provider.py
from constants import ARENA_BONUS_TYPE
from helpers import dependency
from gui.impl.gen import R
from gui.impl import backport
from gui.shared.utils.functions import makeTooltip
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.formatters import text_styles
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from skeletons.gui.game_control import IRTSBattlesController
_RTS_LOCKED_TOOLTIP = makeTooltip(backport.text(R.strings.rts_battles.carousel.lockedTooltip.header()), backport.text(R.strings.rts_battles.carousel.lockedTooltip.body()))

def _getRosterKey(intCD, roster):
    return roster.index(intCD) + 1 if intCD in roster else len(roster) + 1


def _getRosterIndex(intCD, roster):
    return roster.index(intCD) + 1 if intCD in roster else None


class RTSCarouselDataProvider(HangarCarouselDataProvider):
    __rtsController = dependency.descriptor(IRTSBattlesController)

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        baseKey = super(RTSCarouselDataProvider, cls)._vehicleComparisonKey(vehicle)
        isCommander = cls.__rtsController.isCommander()
        resKey = [_getRosterKey(vehicle.intCD, cls.__rtsController.getRoster(ARENA_BONUS_TYPE.RTS).vehicles)] if isCommander else []
        resKey.extend(baseKey)
        return resKey

    def _buildVehicle(self, vehicle):
        result = super(RTSCarouselDataProvider, self)._buildVehicle(vehicle)
        isCommander = self.__rtsController.isCommander()
        rosterIndex = _getRosterIndex(vehicle.intCD, self.__rtsController.getRoster(ARENA_BONUS_TYPE.RTS).vehicles)
        state, _ = vehicle.getState()
        updateDict = {'xpImgSource': '',
         'isEarnCrystals': False,
         'isCrystalsLimitReached': False,
         'rtsRosterIndex': rosterIndex if rosterIndex is not None and isCommander else 0,
         'lockedTooltip': _RTS_LOCKED_TOOLTIP if state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE else ''}
        if state == Vehicle.VEHICLE_STATE.AMMO_NOT_FULL:
            status = backport.text(R.strings.rts_battles.carousel.vehicleStates.ammoNotFull())
            updateDict['infoText'] = updateDict['infoHoverText'] = text_styles.vehicleStatusCriticalText(status)
            updateDict['smallInfoText'] = updateDict['smallInfoHoverText'] = text_styles.stats(status)
            updateDict['infoImgSrc'] = backport.image(R.images.gui.maps.icons.vehicleStates.ammoNotFull())
        result.update(updateDict)
        return result
