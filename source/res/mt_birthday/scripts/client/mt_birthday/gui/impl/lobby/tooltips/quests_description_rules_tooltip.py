# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/tooltips/quests_description_rules_tooltip.py
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillIntsArray
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from mt_birthday.gui.impl.gen.view_models.views.lobby.tooltips.description_rules_tooltip_model import DescriptionRulesTooltipModel

class DescriptionRulesTooltip(ViewImpl):

    def __init__(self, minLevel, maxLevel, battleTypesStr=''):
        settings = ViewSettings(R.views.mt_birthday.lobby.tooltips.DescriptionRulesTooltip(), model=DescriptionRulesTooltipModel())
        self.__minLevel = minLevel
        self.__maxLevel = maxLevel
        self.__battleTypes = [ int(battleType) for battleType in battleTypesStr.split(',') ] if battleTypesStr else []
        super(DescriptionRulesTooltip, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(DescriptionRulesTooltip, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as tx:
            tx.setMinLevel(self.__minLevel)
            tx.setMaxLevel(self.__maxLevel)
            battleTypesModel = tx.getBattleTypes()
            fillIntsArray(self.__battleTypes, battleTypesModel)
            battleTypesModel.invalidate()
