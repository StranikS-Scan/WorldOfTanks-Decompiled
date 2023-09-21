# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/crew_book_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import crew_book
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

class CrewBookTooltipBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(CrewBookTooltipBuilder, self).__init__(tooltipType, linkage, crew_book.CrewBookTooltipDataBlock(contexts.CrewBookContext()))

    def _buildData(self, _advanced, crewBookCD, *args, **kwargs):
        return super(CrewBookTooltipBuilder, self)._buildData(_advanced, crewBookCD)


class CrewBookRestrictedTooltipBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(CrewBookRestrictedTooltipBuilder, self).__init__(tooltipType, linkage, crew_book.CrewBookRestrictedTooltipDataBlock(contexts.CrewBookVehicleContext()))

    def _buildData(self, _advanced, vehicleID, *args, **kwargs):
        return super(CrewBookRestrictedTooltipBuilder, self)._buildData(_advanced, vehicleID)


def getTooltipBuilders():
    return (CrewBookTooltipBuilder(TOOLTIPS_CONSTANTS.CREW_BOOK, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI), CrewBookRestrictedTooltipBuilder(TOOLTIPS_CONSTANTS.CREW_BOOK_RESTRICTED, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI))
