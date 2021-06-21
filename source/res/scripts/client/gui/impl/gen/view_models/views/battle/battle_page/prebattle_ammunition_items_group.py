# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/battle_page/prebattle_ammunition_items_group.py
from gui.impl.gen.view_models.views.battle.battle_page.prebattle_ammunition_setup_selector import PrebattleAmmunitionSetupSelector
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_items_group import AmmunitionItemsGroup

class PrebattleAmmunitionItemsGroup(AmmunitionItemsGroup):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(PrebattleAmmunitionItemsGroup, self).__init__(properties=properties, commands=commands)

    @property
    def setupSelector(self):
        return self._getViewModel(5)

    def _initialize(self):
        super(PrebattleAmmunitionItemsGroup, self)._initialize()
        self._addViewModelProperty('setupSelector', PrebattleAmmunitionSetupSelector())
