# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/royale/carousel_data_provider.py
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TYPES_ORDER_INDICES, getIconResourceName
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
_UNDEFINED_VEHICLE_TYPE = 'undefined'

class RoyaleCarouselDataProvider(HangarCarouselDataProvider):

    def _setBaseCriteria(self):
        self._baseCriteria = REQ_CRITERIA.INVENTORY

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

    def _isWotPlusRentEnabled(self):
        return False

    def _buildVehicle(self, vehicle):
        result = super(RoyaleCarouselDataProvider, self)._buildVehicle(vehicle)
        state, _ = vehicle.getState()
        if vehicle.isOnlyForBattleRoyaleBattles:
            result.update({'label': text_styles.premiumVehicleName(vehicle.userName),
             'tooltip': TOOLTIPS_CONSTANTS.BATTLE_ROYALE_VEHICLE,
             'level': 0,
             'tankType': _UNDEFINED_VEHICLE_TYPE,
             'xpImgSource': '',
             'isUseRightBtn': False})
            iconId = getIconResourceName(vehicle.name)
            iconResId = R.images.gui.maps.icons.battleRoyale.hangar.vehicles.dyn(iconId)
            if iconResId.exists():
                result['icon'] = backport.image(iconResId())
            smallIconResId = R.images.gui.maps.icons.battleRoyale.hangar.vehicles.small.dyn(iconId)
            if smallIconResId.exists():
                result['iconSmall'] = backport.image(smallIconResId())
        elif state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE:
            result['lockedTooltip'] = makeTooltip(backport.text(R.strings.battle_royale.battleRoyaleCarousel.lockedToolTip.header()), backport.text(R.strings.battle_royale.battleRoyaleCarousel.lockedToolTip.body()))
            result['clickEnabled'] = True
        return result
