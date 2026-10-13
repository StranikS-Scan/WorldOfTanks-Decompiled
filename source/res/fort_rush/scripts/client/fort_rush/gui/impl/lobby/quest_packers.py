# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/quest_packers.py
from __future__ import absolute_import
from fort_rush.gui.impl.lobby.bonus_packers import getFortRushMissionBonusPacker
from fort_rush.gui.impl.lobby.bonus_packers import FortRushTokenBonusUIPacker
from gui.shared.missions.packers.events import DailyQuestUIDataPacker, findFirstConditionModel

class FortRushDailyQuestUIDataPacker(DailyQuestUIDataPacker):

    def _getBonusPacker(self):
        packer = getFortRushMissionBonusPacker()
        return packer

    def _resolveQuestIcon(self, model):
        conditionModel = findFirstConditionModel(model.postBattleCondition)
        if conditionModel is None:
            conditionModel = findFirstConditionModel(model.bonusCondition)
            if conditionModel is None:
                return
        model.setIcon(conditionModel.getIconKey())
        return
