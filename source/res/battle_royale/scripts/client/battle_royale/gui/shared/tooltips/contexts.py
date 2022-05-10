# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/shared/tooltips/contexts.py
from collections import namedtuple
from gui.impl.gen.view_models.views.battle_royale.equipment_panel_cmp_rent_states import EquipmentPanelCmpRentStates
from gui.shared.tooltips.contexts import InventoryContext
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleRentVehiclesController
_BattleRoyaleStatusConfiguration = namedtuple('_BattleRoyaleStatusConfiguration', 'isRentNotActive,')

class BattleRoyaleCarouselContext(InventoryContext):
    __rentVehiclesController = dependency.descriptor(IBattleRoyaleRentVehiclesController)

    def getStatusConfiguration(self, item):
        value = super(BattleRoyaleCarouselContext, self).getStatusConfiguration(item)
        state = self.__rentVehiclesController.getRentState(item.intCD)
        isRentNotActive = state in (EquipmentPanelCmpRentStates.STATE_RENT_AVAILABLE, EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_AVAILABLE)
        value.battleRoyale = _BattleRoyaleStatusConfiguration(isRentNotActive)
        return value
