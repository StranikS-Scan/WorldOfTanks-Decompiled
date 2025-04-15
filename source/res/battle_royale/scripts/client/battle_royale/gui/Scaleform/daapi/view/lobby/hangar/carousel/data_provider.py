# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/hangar/carousel/data_provider.py
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TYPES_ORDER_INDICES
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
_UNDEFINED_VEHICLE_TYPE = 'undefined'

class RoyaleCarouselDataProvider(HangarCarouselDataProvider):

    def getVehiclesIntCDs(self):
        vehicledIntCDs = []
        for vehicle in self._vehicles:
            vehicledIntCDs.append(vehicle.intCD)

        return vehicledIntCDs

    def _getAdditionalItemsIndexes(self):
        return []

    def _setBaseCriteria(self):
        self._baseCriteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.BATTLE_ROYALE

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (vehicle.getCustomState() == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE,
         not vehicle.isInInventory,
         not vehicle.isEvent,
         not vehicle.isOnlyForBattleRoyaleBattles,
         not vehicle.isFavorite,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)

    def _isTelecomRentalsEnabled(self):
        return False

    def _buildVehicle(self, vehicle):
        result = super(RoyaleCarouselDataProvider, self)._buildVehicle(vehicle)
        state, _ = vehicle.getState()
        if vehicle.isOnlyForBattleRoyaleBattles:
            vState, _ = vehicle.getState()
            result.update({'label': vehicle.shortUserName,
             'tooltip': TOOLTIPS_CONSTANTS.BATTLE_ROYALE_VEHICLE,
             'level': 0,
             'tankType': vehicle.type,
             'xpImgSource': '',
             'isUseRightBtn': True})
            if vState not in (Vehicle.VEHICLE_STATE.IN_PREBATTLE,
             Vehicle.VEHICLE_STATE.DAMAGED,
             Vehicle.VEHICLE_STATE.DESTROYED,
             Vehicle.VEHICLE_STATE.EXPLODED,
             Vehicle.VEHICLE_STATE.BATTLE):
                result.update({'infoText': '',
                 'smallInfoText': '',
                 'infoImgSrc': ''})
        elif state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE:
            result['lockedTooltip'] = makeTooltip(backport.text(R.strings.battle_royale.battleRoyaleCarousel.lockedToolTip.header()), backport.text(R.strings.battle_royale.battleRoyaleCarousel.lockedToolTip.body()))
            result['clickEnabled'] = True
        return result
