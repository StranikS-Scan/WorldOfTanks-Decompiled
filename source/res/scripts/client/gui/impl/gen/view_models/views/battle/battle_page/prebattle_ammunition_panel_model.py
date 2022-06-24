# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/battle_page/prebattle_ammunition_panel_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.battle.battle_page.prebattle_ammunition_items_group import PrebattleAmmunitionItemsGroup
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_panel_model import AmmunitionPanelModel

class PrebattleAmmunitionPanelModel(AmmunitionPanelModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=6):
        super(PrebattleAmmunitionPanelModel, self).__init__(properties=properties, commands=commands)

    def getSectionGroups(self):
        return self._getArray(6)

    def setSectionGroups(self, value):
        self._setArray(6, value)

    @staticmethod
    def getSectionGroupsType():
        return PrebattleAmmunitionItemsGroup

    def _initialize(self):
        super(PrebattleAmmunitionPanelModel, self)._initialize()
        self._addArrayProperty('sectionGroups', Array())
