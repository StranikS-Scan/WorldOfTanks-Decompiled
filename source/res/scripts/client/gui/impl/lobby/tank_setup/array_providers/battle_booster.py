# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/array_providers/battle_booster.py
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_slot_model import BaseSlotModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_booster_slot_model import BattleBoosterSlotModel
from gui.impl.lobby.tank_setup.array_providers.base import VehicleBaseArrayProvider
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from web.web_client_api.shop.formatters import formatValueToColorTag, COLOR_TAG_CLOSE, COLOR_TAG_OPEN

class BaseBattleBoosterProvider(VehicleBaseArrayProvider):
    __slots__ = ()

    def getItemViewModel(self):
        return BattleBoosterSlotModel()

    def createSlot(self, item, ctx):
        model = super(BaseBattleBoosterProvider, self).createSlot(item, ctx)
        model.setImageName(item.descriptor.iconName)
        isEnough = item.mayPurchaseWithExchange(self._itemsCache.items.stats.money, self._itemsCache.items.shop.exchangeRate)
        model.setIsBuyMoreVisible(not item.isHidden)
        model.setIsBuyMoreDisabled(not isEnough)
        self._fillHighlights(model, item)
        self._fillBuyPrice(model, item)
        return model

    def updateSlot(self, model, item, ctx):
        super(BaseBattleBoosterProvider, self).updateSlot(model, item, ctx)
        isInstalledOrMounted = item in self._getCurrentLayout() or item in self._getInstalledLayout()
        self._fillStatus(model, item, ctx.slotID, isInstalledOrMounted)
        self._fillBuyStatus(model, item, isInstalledOrMounted)
        self._fillDescription(model, item)

    def _fillHighlights(self, model, item):
        model.setHighlightType(ItemHighlightTypes.BATTLE_BOOSTER)
        model.setOverlayType(ItemHighlightTypes.BATTLE_BOOSTER)

    def _fillStatus(self, model, item, slotID, isInstalledOrMounted):
        super(BaseBattleBoosterProvider, self)._fillStatus(model, item, slotID, isInstalledOrMounted)
        if not item.isAffectsOnVehicle(self._getVehicle()):
            model.setIsLocked(True)

    def _fillDescription(self, model, item):
        raise NotImplementedError

    @classmethod
    def _getItemTypeID(cls):
        return (GUI_ITEM_TYPE.BATTLE_BOOSTER,)

    def _getEquipment(self):
        return self._getVehicle().battleBoosters

    def _getItemSortKey(self, item, ctx):
        return (item.getBuyPrice().price, item.userName)


class OptDeviceBattleBoosterProvider(BaseBattleBoosterProvider):
    __slots__ = ()

    def _getItemCriteria(self):
        invVehicles = self._itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
        installedSet = set((booster for veh in invVehicles.itervalues() for booster in veh.battleBoosters.installed.getIntCDs()))
        return REQ_CRITERIA.CUSTOM(lambda item: not item.isCrewBooster() and (not item.isHidden or item.isInInventory or item.intCD in installedSet))

    def _fillDescription(self, model, item):
        model.setDescription(item.getOptDeviceBoosterDescription(self._getVehicle(), formatValueToColorTag))


class CrewBattleBoosterProvider(BaseBattleBoosterProvider):
    __slots__ = ()

    def _getItemCriteria(self):
        return REQ_CRITERIA.BATTLE_BOOSTER.CREW_EFFECT

    def _fillHighlights(self, model, item):
        super(CrewBattleBoosterProvider, self)._fillHighlights(model, item)
        if not item.isAffectedSkillLearnt(self._getVehicle()):
            model.setOverlayType(ItemHighlightTypes.BATTLE_BOOSTER_REPLACE)

    def _fillDescription(self, model, item):
        skillLearnt = item.isAffectedSkillLearnt(self._getVehicle())
        model.setDescription(item.getCrewBoosterDescription(not skillLearnt, {'colorTagOpen': COLOR_TAG_OPEN,
         'colorTagClose': COLOR_TAG_CLOSE}))
