# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_congrats_types.py
from frameworks.wulf import ViewModel

class LootCongratsTypes(ViewModel):
    __slots__ = ()
    CONGRAT_TYPE_BLUEPRINT = 'BlueprintFinalFragmentCongrats'
    CONGRAT_TYPE_BLUEPRINT_PART = 'BlueprintVehicleFragmentCongrats'
    CONGRAT_TYPE_VEHICLE = 'VehicleLootBoxCongrats'
    CONGRAT_TYPE_STYLE = 'StyleLootBoxCongrats'
    CONGRAT_TYPE_TANKMAN = 'TankmanLootBoxCongrats'
    CONGRAT_TYPE_GUEST_C = 'GuestCRewardKitCongrats'
    CONGRAT_TYPE_MODERNIZED_EQUIPMENT = 'ModernizedEquipmentRewardKitCongrats'
    INIT_CONGRAT_TYPE_USUAL = 'UsualCongrats'
    INIT_CONGRAT_TYPE_PROGRESSIVE_REWARDS = 'ProgressiveRewardCongrats'
    INIT_CONGRAT_TYPE_CREW_BOOKS = 'CrewBookCongrats'
    INIT_CONGRAT_TYPE_LOOTBOX = 'LootBoxCongrats'
    INIT_CONGRAT_TYPE_EPIC_REWARDS = 'EpicRewardCongrats'
    INIT_CONGRAT_TYPE_BATTLE_PASS = 'BattlePassCongrats'
    INIT_CONGRAT_TYPE_AC_EMAIL_CONFIRMATION = 'ACEmailConfirmation'

    def __init__(self, properties=0, commands=0):
        super(LootCongratsTypes, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(LootCongratsTypes, self)._initialize()
