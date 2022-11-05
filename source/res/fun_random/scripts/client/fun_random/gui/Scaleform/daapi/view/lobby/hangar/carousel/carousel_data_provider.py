# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/hangar/carousel/carousel_data_provider.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from constants import ARENA_BONUS_TYPE, Configs
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass.carousel_data_provider import BattlePassCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.carousel_helpers import getUnsuitable2queueTooltip
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TYPES_ORDER_INDICES
from helpers import server_settings

class FunRandomCarouselDataProvider(BattlePassCarouselDataProvider, FunSubModesWatcher):

    def __init__(self, carouselFilter, itemsCache):
        super(FunRandomCarouselDataProvider, self).__init__(carouselFilter, itemsCache)
        self.__isCrystalsFarmEnabled = self.__isCrystalsFarmPossible()

    def _populate(self):
        super(FunRandomCarouselDataProvider, self)._populate()
        self._lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged

    def _dispose(self):
        self._lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        super(FunRandomCarouselDataProvider, self)._dispose()

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (cls._isSuitableForQueue(vehicle),
         not vehicle.isInInventory,
         not vehicle.isEvent,
         not vehicle.isOnlyForBattleRoyaleBattles,
         not vehicle.isFavorite,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)

    def _buildVehicle(self, vehicle):
        result = super(FunRandomCarouselDataProvider, self)._buildVehicle(vehicle)
        state, _ = vehicle.getState()
        if state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE:
            self.__specifyLockedTooltip(result, vehicle)
        result['tooltip'] = TOOLTIPS_CONSTANTS.FUN_RANDOM_CAROUSEL_VEHICLE
        result['isEarnCrystals'] = result['isEarnCrystals'] and self.__isCrystalsFarmEnabled
        if not ARENA_BONUS_TYPE_CAPS.checkAny(ARENA_BONUS_TYPE.FUN_RANDOM, ARENA_BONUS_TYPE_CAPS.DAILY_MULTIPLIED_XP):
            result['xpImgSource'] = ''
        return result

    def _isBattlePassHidden(self, vehicle):
        result = super(FunRandomCarouselDataProvider, self)._isBattlePassHidden(vehicle)
        return result or not self.battlePassController.isGameModeEnabled(ARENA_BONUS_TYPE.FUN_RANDOM)

    def __isCrystalsFarmPossible(self):
        config = self._serverSettings.getCrystalRewardConfig()
        return config.isCrystalEarnPossible(ARENA_BONUS_TYPE.FUN_RANDOM)

    @server_settings.serverSettingsChangeListener(Configs.CRYSTAL_REWARDS_CONFIG.value)
    def __onServerSettingsChanged(self, *_, **_FunRandomCarouselDataProvider__kwargs):
        self.__isCrystalsFarmEnabled = self.__isCrystalsFarmPossible()

    @hasDesiredSubMode()
    def __specifyLockedTooltip(self, result, vehicle):
        validationResult = self.getDesiredSubMode().isSuitableVehicle(vehicle)
        if validationResult is not None:
            resPath = R.strings.fun_random.funRandomCarousel.lockedTooltip
            result['lockedTooltip'] = getUnsuitable2queueTooltip(validationResult, resPath)
        return
