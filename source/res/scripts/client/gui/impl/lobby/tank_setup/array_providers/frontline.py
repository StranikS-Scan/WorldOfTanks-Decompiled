# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/array_providers/frontline.py
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_ability_slot_model import BattleAbilitySlotModel
from gui.impl.lobby.tank_setup.array_providers.base import VehicleBaseArrayProvider
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, i18n
from skeletons.gui.game_control import IEpicBattleMetaGameController

class BattleAbilityProvider(VehicleBaseArrayProvider):
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ()

    def getItemViewModel(self):
        return BattleAbilitySlotModel()

    def createSlot(self, item, ctx):
        model = super(BattleAbilityProvider, self).createSlot(item, ctx)
        model.setDescription(i18n.makeString(item.shortDescription))
        model.setImageName(item.descriptor.iconName)
        return model

    def updateSlot(self, model, item, ctx):
        super(BattleAbilityProvider, self).updateSlot(model, item, ctx)
        model.setLevel(item.level if item.isUnlocked else 0)

    @classmethod
    def _getItemTypeID(cls):
        return (GUI_ITEM_TYPE.BATTLE_ABILITY,)

    def _getCriteria(self):
        skillItemIDs = []
        allSkills = self.__epicMetaGameCtrl.getAllSkillsInformation().values()
        for skillInfo in allSkills:
            skillExample = skillInfo.getMaxUnlockedSkillLevel() or skillInfo.levels[skillInfo.maxLvl]
            skillItemIDs.append(skillExample.eqID)

        return REQ_CRITERIA.CUSTOM(lambda item: item.innationID in skillItemIDs)

    def _getItemSortKey(self, item, ctx):
        return (item.getBuyPrice().price, item.userName)
