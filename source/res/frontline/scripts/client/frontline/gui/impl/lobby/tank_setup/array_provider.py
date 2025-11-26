# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/tank_setup/array_provider.py
import typing
from WeakMixin import WeakMixin, Tapped
from constants import PLAYER_RANK
from epic_constants import CATEGORIES_ORDER
from frontline.gui.impl.gen.view_models.views.lobby.components.loadout.battle_ability_slot_model import BattleAbilitySlotModel
from gui.impl.lobby.tank_setup.array_providers.base import VehicleBaseArrayProvider, BaseVehSectionContext
from gui.impl.lobby.tank_setup.tank_setup_helper import NONE_ID
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.artefacts import BattleAbility
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers.epic_game import searchRankForSlot
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IEpicBattleMetaGameController
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array

class BattleAbilityMixin(WeakMixin, Tapped):

    @classmethod
    def fromBattleAbility(cls, item, **kwargs):
        return BattleAbilityMixin(item).tap(**kwargs) if isinstance(item, BattleAbility) else None


class BattleAbilityProvider(VehicleBaseArrayProvider):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def createSlot(self, item, ctx):
        skillInfo = item.skillData.getSkillInfo()
        category = item.category
        model = super(BattleAbilityProvider, self).createSlot(item, ctx)
        model.setDescription(skillInfo.shortDescr)
        model.setImageName(item.descriptor.iconName)
        model.setCost(item.price)
        model.setSkillId(item.skillData.skillID)
        model.setCategory(category)
        model.setTargetSlotId(CATEGORIES_ORDER.index(category))
        return model

    def fillArray(self, array, ctx, itemFilter=None):
        items = self.getItems()
        array.clear()
        for item in items:
            itemModel = self.createSlot(item, ctx)
            self.updateSlot(itemModel, item, ctx)
            array.addViewModel(itemModel)

        array.invalidate()

    def getItemViewModel(self):
        return BattleAbilitySlotModel()

    def getItemsList(self):
        items = self._itemsCache.items.getItems(self._getItemTypeID(), self._getCriteria()).values()
        epicSkills = self._getEpicSkills()
        abilities = []
        for item in items:
            skill = epicSkills[item.innationID]
            category = skill.category
            abilities.append(BattleAbilityMixin.fromBattleAbility(item, isActivated=skill.isActivated, price=skill.price, category=category, rank=self._getRankIconName(category), skillData=skill))

        return abilities

    def updateArray(self, array, ctx):
        items = self.getItems()
        idsToUpdate = {arrayModel.getIntCD():arrayModel for arrayModel in array}
        for item in items:
            if item.intCD in idsToUpdate:
                self.updateSlot(idsToUpdate[item.intCD], item, ctx)

    def updateSlot(self, model, item, ctx):
        super(BattleAbilityProvider, self).updateSlot(model, item, ctx)
        self._fillStatus(model, item, ctx.slotID)
        model.setRank(self._getRankIconName(item.category))
        if not self.__epicMetaGameCtrl.isCurVehicleSuitable():
            model.setInstalledSlotId(NONE_ID)

    def _fillStatus(self, model, item, slotID):
        model.setIsDisabled(not item.isActivated)

    def _getCriteria(self):
        return REQ_CRITERIA.CUSTOM(lambda item: item.innationID in self._getEpicSkills().keys())

    def _getEpicSkills(self):
        allSkills = self.__epicMetaGameCtrl.getAllSkillsInformation().values()
        return {skill.getSkillInfo().eqID:skill for skill in allSkills}

    @classmethod
    def _getItemTypeID(cls):
        return (GUI_ITEM_TYPE.BATTLE_ABILITY,)

    def _getRankIconName(self, category):
        rankIconName = ''
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
        currentRank = None
        if playerDataComp is not None:
            currentRank = playerDataComp.playerRank - 1 if playerDataComp.playerRank is not None else 0
        unlockSlotOrder = self.__epicMetaGameCtrl.getAbilitySlotsUnlockOrder(self._getVehicle().descriptor.type)
        slotRank = searchRankForSlot(CATEGORIES_ORDER.index(category), unlockSlotOrder)
        if slotRank and (currentRank is None or currentRank < slotRank):
            slotRank += 1
            rankIconName = PLAYER_RANK.NAMES[slotRank]
        return rankIconName
