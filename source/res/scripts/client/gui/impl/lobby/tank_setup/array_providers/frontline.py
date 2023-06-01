# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/array_providers/frontline.py
from WeakMixin import WeakMixin, Tapped
from epic_constants import CATEGORIES_ORDER
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_ability_slot_model import BattleAbilitySlotModel
from gui.impl.lobby.tank_setup.array_providers.base import VehicleBaseArrayProvider, BaseVehSectionContext
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.artefacts import BattleAbility
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
import typing
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array

class BattleAbilityMixin(WeakMixin, Tapped):

    @classmethod
    def fromBattleAbility(cls, item, **kwargs):
        return BattleAbilityMixin(item).tap(**kwargs) if isinstance(item, BattleAbility) else None


class BattleAbilityProvider(VehicleBaseArrayProvider):
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ('__abilities',)

    def __init__(self, interactor):
        self.updateAbiblities()
        super(BattleAbilityProvider, self).__init__(interactor)

    def getItemsList(self):
        return self.__getAbilities()

    def getItemViewModel(self):
        return BattleAbilitySlotModel()

    def fillArray(self, array, ctx, itemFilter=None):
        items = self.__getAbilities()
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
        skillInfo = item.skillData.getSkillInfo()
        model = super(BattleAbilityProvider, self).createSlot(item, ctx)
        model.setDescription(skillInfo.shortDescr)
        model.setImageName(item.descriptor.iconName)
        model.setCost(item.price)
        model.setSkillId(item.skillData.skillID)
        model.setCategory(item.category)
        model.setTargetSlotId(CATEGORIES_ORDER.index(item.category))
        model.setCategory(item.category)
        return model

    def updateSlot(self, model, item, ctx):
        super(BattleAbilityProvider, self).updateSlot(model, item, ctx)
        self._fillStatus(model, item, ctx.slotID)

    def _fillStatus(self, model, item, slotID):
        model.setIsDisabled(not item.isActivated)

    @classmethod
    def _getItemTypeID(cls):
        return (GUI_ITEM_TYPE.BATTLE_ABILITY,)

    def _getCriteria(self):
        return REQ_CRITERIA.CUSTOM(lambda item: item.innationID in self.__getEpicSkills().keys())

    def __getAbilities(self):
        return self.__abilities

    def updateAbiblities(self):
        items = self._itemsCache.items.getItems(self._getItemTypeID(), self._getCriteria()).values()
        epicSkills = self.__getEpicSkills()
        self.__abilities = []
        for item in items:
            skill = epicSkills[item.innationID]
            self.__abilities.append(BattleAbilityMixin.fromBattleAbility(item, isActivated=skill.isActivated, price=skill.price, category=skill.category, skillData=skill))

    def __getEpicSkills(self):
        allSkills = self.__epicMetaGameCtrl.getAllSkillsInformation().values()
        return {skill.getSkillInfo().eqID:skill for skill in allSkills}
