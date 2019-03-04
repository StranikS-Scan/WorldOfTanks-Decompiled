# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/crew_skin_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import crew_skin
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

class CrewSkinTooltipBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(CrewSkinTooltipBuilder, self).__init__(tooltipType, linkage, crew_skin.CrewSkinTooltipDataBlock(contexts.CrewSkinContext()))

    def _buildData(self, _advanced, crewSkinID, *args, **kwargs):
        return super(CrewSkinTooltipBuilder, self)._buildData(_advanced, crewSkinID)


class CrewSkinNoAvailableSkinsTooltipBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(CrewSkinNoAvailableSkinsTooltipBuilder, self).__init__(tooltipType, linkage, crew_skin.CrewSkinNoAvailableSkinsTooltipDataBlock(contexts.CrewSkinTankmanContext()))

    def _buildData(self, _advanced, tankmanID, crewSkinID, *args, **kwargs):
        return super(CrewSkinNoAvailableSkinsTooltipBuilder, self)._buildData(_advanced, tankmanID, crewSkinID)


class CrewSkinRestrictedTooltipBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(CrewSkinRestrictedTooltipBuilder, self).__init__(tooltipType, linkage, crew_skin.CrewSkinRestrictedTooltipDataBlock(contexts.CrewSkinTankmanContext()))

    def _buildData(self, _advanced, tankmanID, crewSkinID, *args, **kwargs):
        return super(CrewSkinRestrictedTooltipBuilder, self)._buildData(_advanced, tankmanID, crewSkinID)


class CrewSkinSoundTooltipBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(CrewSkinSoundTooltipBuilder, self).__init__(tooltipType, linkage, crew_skin.CrewSkinSoundTooltipDataBlock(contexts.CrewSkinTankmanContext()))

    def _buildData(self, _advanced, tankmanID, crewSkinID, *args, **kwargs):
        return super(CrewSkinSoundTooltipBuilder, self)._buildData(_advanced, tankmanID, crewSkinID)


def getTooltipBuilders():
    return (CrewSkinTooltipBuilder(TOOLTIPS_CONSTANTS.CREW_SKIN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     CrewSkinNoAvailableSkinsTooltipBuilder(TOOLTIPS_CONSTANTS.CREW_SKIN_NO_AVAILABLE_SKINS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     CrewSkinRestrictedTooltipBuilder(TOOLTIPS_CONSTANTS.CREW_SKIN_RESTRICTED, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     CrewSkinSoundTooltipBuilder(TOOLTIPS_CONSTANTS.CREW_SKIN_SOUND, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI))
