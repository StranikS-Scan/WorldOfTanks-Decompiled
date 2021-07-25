# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/crew_skin.py
import SoundGroups
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.impl.gen import R
from gui.impl import backport
from helpers import dependency
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.gui_items.crew_skin import localizedFullName, Rarity, getCrewSkinIconBig
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from skeletons.gui.lobby_context import ILobbyContext
from nations import NAMES
_MAX_USERS_DISPLAYED = 10

def _longStringListEllipsisCutoff(fstring, strings, allowedLen):
    return fstring.join(strings[:allowedLen]) + '...' if len(strings) > allowedLen else fstring.join(strings)


class CrewSkinTooltipDataBlock(BlocksTooltipData):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, context):
        super(CrewSkinTooltipDataBlock, self).__init__(context, TOOLTIP_TYPE.CREW_SKIN)
        self._setContentMargin(bottom=8)
        self._setWidth(320)

    def _packBlocks(self, *args, **kwargs):
        items = super(CrewSkinTooltipDataBlock, self)._packBlocks()
        item = self.context.buildItem(*args, **kwargs)
        topBlock = []
        topBlock.append(formatters.packTextBlockData(text=text_styles.highTitle(localizedFullName(item))))
        topBlock.append(formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.item_types.crewSkins.itemType.dyn(Rarity.STRINGS[item.getRarity()])()))))
        topBlock.append(formatters.packImageTextBlockData(img=RES_ICONS.MAPS_ICONS_TOOLTIP_TOOLTIP_TANKMAN_BACK, padding=formatters.packPadding(18)))
        if self.lobbyContext.getServerSettings().isCrewSkinsEnabled():
            topBlock.append(formatters.packImageTextBlockData(img=getCrewSkinIconBig(item.getIconID()), imgPadding=formatters.packPadding(left=60), padding=formatters.packPadding(-142)))
        topBlock.append(formatters.packTextBlockData(text=text_styles.main(item.getDescription()), padding=formatters.packPadding(14)))
        items.append(formatters.packBuildUpBlockData(topBlock))
        block = []
        block.append(formatters.packTextParameterBlockData(name=text_styles.stats(str(len(item.getDetachmentIDs()))), value=text_styles.main(backport.text(R.strings.crew_skins.feature.inUse())), valueWidth=115))
        block.append(formatters.packTextParameterBlockData(name=text_styles.stats('{free}({max})'.format(free=item.getFreeCount(), max=9999)), value=text_styles.main(backport.text(R.strings.crew_skins.feature.inStorage())), valueWidth=115))
        restrictions = []
        if item.getNation() is not None:
            restrictions.append(backport.text(R.strings.nations.dyn(item.getNation())()))
        if restrictions:
            restrictionText = ', '.join(restrictions)
        else:
            restrictionText = backport.text(R.strings.tooltips.crewSkins.noRestrictions())
        block.append(formatters.packTextParameterBlockData(name=text_styles.stats(restrictionText), value=text_styles.main(backport.text(R.strings.tooltips.crewSkins.restrictions())), valueWidth=115))
        items.append(formatters.packBuildUpBlockData(block))
        skinUsersRoleAndVehicle = ''
        if skinUsersRoleAndVehicle:
            usedBlock = []
            usedBlock.append(formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.crewSkins.inUse()))))
            usedBlock.append(formatters.packTextBlockData(text=text_styles.main(_longStringListEllipsisCutoff(', ', skinUsersRoleAndVehicle, _MAX_USERS_DISPLAYED))))
            items.append(formatters.packBuildUpBlockData(usedBlock))
        return items


class CrewSkinNoAvailableSkinsTooltipDataBlock(BlocksTooltipData):

    def __init__(self, context):
        super(CrewSkinNoAvailableSkinsTooltipDataBlock, self).__init__(context, TOOLTIP_TYPE.CREW_SKIN)
        self._setContentMargin(bottom=8)
        self._setWidth(372)

    def _packBlocks(self, *args, **kwargs):
        items = super(CrewSkinNoAvailableSkinsTooltipDataBlock, self)._packBlocks()
        topBlock = []
        topBlock.append(formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.crewSkins.allUsedHeader()))))
        topBlock.append(formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.crewSkins.allUsedDescr()))))
        items.append(formatters.packBuildUpBlockData(topBlock))
        skinUsersRoleAndVehicle = ''
        usedBlock = []
        usedBlock.append(formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.crewSkins.inUse()))))
        usedBlock.append(formatters.packTextBlockData(text=text_styles.main(_longStringListEllipsisCutoff(', ', skinUsersRoleAndVehicle, _MAX_USERS_DISPLAYED))))
        items.append(formatters.packBuildUpBlockData(usedBlock))
        return items


class CrewSkinRestrictedTooltipDataBlock(BlocksTooltipData):

    def __init__(self, context):
        super(CrewSkinRestrictedTooltipDataBlock, self).__init__(context, TOOLTIP_TYPE.CREW_SKIN)
        self._setContentMargin(bottom=8)
        self._setWidth(320)

    def _packBlocks(self, *args, **kwargs):
        items = super(CrewSkinRestrictedTooltipDataBlock, self)._packBlocks()
        skinTankmanContext = self.context.buildItem(*args, **kwargs)
        crewSkin = skinTankmanContext.crewSkin
        tankman = skinTankmanContext.tankman
        block = []
        block.append(formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.crewSkins.restrictions.header()))))
        block.append(formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.crewSkins.restrictions()))))
        if crewSkin.getNation() is not None:
            text = backport.text(R.strings.nations.dyn(crewSkin.getNation())())
            if crewSkin.getNation() != NAMES[tankman.nationID]:
                highlight = text_styles.alert(text)
            else:
                highlight = text_styles.main(text)
            block.append(formatters.packTextBlockData(text=u'\u2022 ' + highlight))
        items.append(formatters.packBuildUpBlockData(block))
        return items


class CrewSkinSoundTooltipDataBlock(BlocksTooltipData):

    def __init__(self, context):
        super(CrewSkinSoundTooltipDataBlock, self).__init__(context, TOOLTIP_TYPE.CREW_SKIN)
        self._setContentMargin(bottom=8)
        self._setWidth(320)

    def _packBlocks(self, *args, **kwargs):
        items = super(CrewSkinSoundTooltipDataBlock, self)._packBlocks()
        tankman = self.context.buildItem(*args, **kwargs).tankman
        topBlock = []
        topBlock.append(formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.crewSkins.sound()))))
        topBlock.append(formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.crewSkins.soundHeader()))))
        if tankman.role != Tankman.ROLES.COMMANDER:
            topBlock.append(formatters.packImageTextBlockData(img=RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON, imgPadding={'left': -3,
             'top': -2}, txtOffset=20, padding=formatters.packPadding(bottom=0, top=8, left=0), desc=text_styles.alert(backport.text(R.strings.tooltips.crewSkins.soundWarningDescr2()))))
        elif not SoundGroups.g_instance.soundModes.currentNationalPreset[1]:
            topBlock.append(formatters.packImageTextBlockData(img=RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON, imgPadding={'left': -3,
             'top': -2}, txtOffset=20, padding=formatters.packPadding(bottom=0, top=8, left=0), desc=text_styles.alert(backport.text(R.strings.tooltips.crewSkins.soundWarningDescr1()))))
        items.append(formatters.packBuildUpBlockData(topBlock))
        infoBlock = []
        infoBlock.append(formatters.packImageTextBlockData(img=RES_ICONS.MAPS_ICONS_LIBRARY_INFO, imgPadding={'left': -3,
         'top': -2}, txtOffset=20, desc=text_styles.stats(backport.text(R.strings.tooltips.crewSkins.soundInfo()))))
        infoBlock.append(formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.crewSkins.soundInfoDescr())), padding=formatters.packPadding(left=20)))
        items.append(formatters.packBuildUpBlockData(infoBlock))
        return items
