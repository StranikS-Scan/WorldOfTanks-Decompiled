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
    CREWSKINS_COMPENSATION = 'CrewSkinsCompensationRenderer'
    VEHICLE_COMPENSATION = 'VehicleCompensationRenderer'
    VEHICLE_COMPENSATION_WITHOUT_ANIMATION = 'VehicleCompensationWithoutAnimationRenderer'
    BLUEPRINT_FINAL_FRAGMENT = 'BlueprintFinalFragmentRenderer'
    CREW_BOOK = 'CrewBookRenderer'
    NEW_YEAR_TOY = 'LootNewYearToyRenderer'
    NEW_YEAR_FRAGMENTS = 'LootNewYearFragmentsRenderer'
    NEW_YEAR_FRAGMENTS_COMPENSATION = 'LootNewYearFragmentsCompensationRenderer'
    NEW_YEAR_ALBUM = 'LootNewYearAlbumRenderer'

    def __init__(self, properties=0, commands=0):
        super(LootRendererTypes, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(LootRendererTypes, self)._initialize()
