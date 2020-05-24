# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/ranked/carousel_data_provider.py
from gui import GUI_NATIONS_ORDER_INDEX
from gui.impl.gen import R
from gui.impl import backport
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TYPES_ORDER_INDICES, getTypeUserName
from gui.shared.utils.functions import makeTooltip
from gui.shared.formatters import text_styles
from gui.shared.formatters.ranges import toRomanRangeString
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedCarouselDataProvider(HangarCarouselDataProvider):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (not cls._isSuitableForQueue(vehicle),
         not vehicle.isInInventory,
         not vehicle.isEvent,
         not vehicle.isFavorite,
         not cls.__rankedController.hasVehicleRankedBonus(vehicle.intCD),
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)

    def _buildVehicle(self, vehicle):
        result = super(RankedCarouselDataProvider, self)._buildVehicle(vehicle)
        result['hasRankedBonus'] = self.__rankedController.hasVehicleRankedBonus(vehicle.intCD)
        state, _ = vehicle.getState()
        suitResult = self.__rankedController.isSuitableVehicle(vehicle)
        if state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE and suitResult is not None:
            header, body = ('', '')
            resShortCut = R.strings.ranked_battles.rankedBattlesCarousel.lockedTooltip
            if suitResult.restriction == PRE_QUEUE_RESTRICTION.LIMIT_LEVEL:
                levelStr = toRomanRangeString(suitResult.ctx['levels'])
                levelSubStr = backport.text(resShortCut.vehLvl.levelSubStr(), levels=levelStr)
                header = backport.text(resShortCut.vehLvl.header())
                body = backport.text(resShortCut.vehLvl.body(), levelSubStr=levelSubStr)
            elif suitResult.restriction == PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_TYPE:
                typeSubStr = text_styles.neutral(suitResult.ctx['forbiddenType'])
                header = backport.text(resShortCut.vehType.header())
                body = backport.text(resShortCut.vehType.body(), forbiddenType=typeSubStr)
            elif suitResult.restriction == PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_CLASS:
                classSubStr = text_styles.neutral(getTypeUserName(suitResult.ctx['forbiddenClass'], False))
                header = backport.text(resShortCut.vehClass.header())
                body = backport.text(resShortCut.vehClass.body(), forbiddenClass=classSubStr)
            result['lockedTooltip'] = makeTooltip(header, body)
            result['clickEnabled'] = True
            result['hasRankedBonus'] = False
        return result
