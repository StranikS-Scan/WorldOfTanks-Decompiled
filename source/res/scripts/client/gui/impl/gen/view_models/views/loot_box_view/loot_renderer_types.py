# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_renderer_types.py
from frameworks.wulf import ViewModel

class LootRendererTypes(ViewModel):
    __slots__ = ()
    DEF = 'LootDefRenderer'
    VIDEO = 'LootVideoRenderer'
    VEHICLE = 'LootVehicleRenderer'
    VEHICLE_VIDEO = 'LootVehicleVideoRenderer'
    ANIMATED = 'LootAnimatedRenderer'
    CONVERSION = 'LootConversionRenderer'
    COMPENSATION = 'LootCompensationRenderer'
    VEHICLE_COMPENSATION = 'VehicleCompensationRenderer'
    VEHICLE_COMPENSATION_WITHOUT_ANIMATION = 'VehicleCompensationWithoutAnimationRenderer'
    NEW_YEAR_TOY = 'LootNewYearToyRenderer'
    NEW_TEAR_FRAGMENTS = 'LootNewYearFragmentsRenderer'

    def _initialize(self):
        super(LootRendererTypes, self)._initialize()
