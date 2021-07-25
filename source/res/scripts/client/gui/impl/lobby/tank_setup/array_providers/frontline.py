# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/array_providers/frontline.py
from WeakMixin import WeakMixin, Tapped
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_ability_slot_model import BattleAbilitySlotModel
from gui.impl.lobby.tank_setup.array_providers.base import VehicleBaseArrayProvider, BaseVehSectionContext
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.artefacts import BattleAbility
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, i18n
from items.components.supply_slot_categories import SlotCategories
from skeletons.gui.game_control import IEpicBattleMetaGameController

class BattleAbilityMixin(WeakMixin, Tapped):

    @classmethod
    def fromBattleAbility(cls, item, tags, isActivated):
        return BattleAbilityMixin(item).tap(subTags=tags, isActivated=isActivated) if isinstance(item, BattleAbility) else None

    @property
    def tags(self):
        return self.__target__.tags | set(self.subTags)

    @property
    def slotCategory(self):
        return tuple(SlotCategories.ALL.intersection(self.tags))


class BattleAbilityProvider(VehicleBaseArrayProvider):
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def getItemsList(self):
        return self.__getAbilities()

    def getItemViewModel(self):
        return BattleAbilitySlotModel()

    def fillArray(self, array, ctx, itemFilter=None):
        items = self.__filter(self.__getAbilities(), ctx.slotID)
        self._sortItems(items, ctx)
        array.clear()
        for item in items:
            itemModel = self.createSlot(item, ctx)
            self.updateSlot(itemModel, item, ctx)
            array.addViewModel(itemModel)

        array.invalidate()

    def updateArray(self, array, ctx):
        items = self.__getAbilities()
        idsToUpdate = {arrayModel.getIntCD():arrayModel for arrayModel in array}
        for item in items:
            if item.intCD in idsToUpdate:
                self.updateSlot(idsToUpdate[item.intCD], item, ctx)

    def createSlot(self, item, ctx):
        model = super(BattleAbilityProvider, self).createSlot(item, ctx)
        model.setDescription(i18n.makeString(item.shortDescription))
        model.setImageName(item.descriptor.iconName)
        model.setCategory(str(item.slotCategory[0]) if item.slotCategory is not None else '')
        return model

    def updateSlot(self, model, item, ctx):
        super(BattleAbilityProvider, self).updateSlot(model, item, ctx)
        isInstalledOrMounted = item in self._getCurrentLayout() or item in self._getInstalledLayout()
        self._fillStatus(model, item, ctx.slotID, isInstalledOrMounted)

    def _fillStatus(self, model, item, slotID, isInstalledOrMounted):
        model.setIsDisabled(not item.isActivated)
        model.setIsLocked(not item.isActivated)

    @classmethod
    def _getItemTypeID(cls):
        return (GUI_ITEM_TYPE.BATTLE_ABILITY,)

    def _getCriteria(self):
        return REQ_CRITERIA.CUSTOM(lambda item: item.innationID in self.__getEpicSkills().keys())

    def _getItemSortKey(self, item, ctx):
        return ('default' not in item.tags, 'regenerationKit' in item.name, item.userName)

    def __getAbilities(self):
        items = self._itemsCache.items.getItems(self._getItemTypeID(), self._getCriteria()).values()
        epicSkills = self.__getEpicSkills()
        result = []
        for item in items:
            result.append(BattleAbilityMixin.fromBattleAbility(item, epicSkills[item.innationID].tags, epicSkills[item.innationID].isActivated))

        return result

    def __getEpicSkills(self):
        allSkills = self.__epicMetaGameCtrl.getAllSkillsInformation().values()
        return {skill.getSkillInfo().eqID:skill for skill in allSkills}

    def __filter(self, items, slotID):
        veh = self._getVehicle()
        slots = veh.battleAbilities.slots
        slotsOrder = self.__epicMetaGameCtrl.getAbilitySlotsOrder(veh.descriptor.type)
        if slotID >= len(slotsOrder):
            return items
        sID = slotsOrder[slotID]
        result = []
        for slot in slots:
            if sID != slot.slotID:
                continue
            categories = SlotCategories.ALL
            slotCategory = categories.intersection(slot.tags)
            for item in items:
                if slotCategory.issubset(item.tags):
                    result.append(item)

        return result
