# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_congrats_types.py
from frameworks.wulf import ViewModel

class LootCongratsTypes(ViewModel):
    __slots__ = ()
    CONGRAT_TYPE_BLUEPRINT = 'BlueprintFinalFragmentCongrats'
    CONGRAT_TYPE_BLUEPRINT_PART = 'BlueprintVehicleFragmentCongrats'
    INIT_CONGRAT_TYPE_USUAL = 'UsualCongrats'
    INIT_CONGRAT_TYPE_PROGRESSIVE_REWARDS = 'ProgressiveRewardCongrats'
    INIT_CONGRAT_TYPE_CREW_BOOKS = 'CrewBookCongrats'

    def _initialize(self):
        super(LootCongratsTypes, self)._initialize()
