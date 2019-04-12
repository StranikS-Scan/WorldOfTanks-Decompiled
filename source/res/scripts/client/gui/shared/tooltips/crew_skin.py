# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/crew_skin.py
from skeletons.gui.shared import IItemsCache
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from helpers import i18n
from helpers import dependency
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.gui_items.Tankman import getCrewSkinIconBig
from gui.shared.gui_items.crew_skin import GenderRestrictionsLocals, RarityLocals, localizedFullName
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.NATIONS import NATIONS
from items.components.crewSkins_constants import TANKMAN_SEX
from skeletons.gui.lobby_context import ILobbyContext
from nations import NAMES
_MAX_USERS_DISPLAYED = 10

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _skinUsersRoleAndVehicleText(fstring, item, itemsCache=None):
    return [ fstring.format(role=i18n.makeString(ITEM_TYPES.tankman_roles(tankman.role)), vehicle=itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr).shortUserName) for invID, tankman in itemsCache.items.getTankmen().iteritems() if invID in item.getTankmenIDs() ]


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
        topBlock.append(formatters.packTextBlockData(text=text_styles.main(i18n.makeString(RarityLocals.LOCALES[item.getRarity()]))))
        topBlock.append(formatters.packImageTextBlockData(img=RES_ICONS.MAPS_ICONS_TOOLTIP_TOOLTIP_TANKMAN_BACK, padding=formatters.packPadding(18)))
        if self.lobbyContext.getServerSettings().isCrewSkinsEnabled():
            topBlock.append(formatters.packImageTextBlockData(img=getCrewSkinIconBig(item.getIconID()), imgPadding=formatters.packPadding(left=60), padding=formatters.packPadding(-142)))
        topBlock.append(formatters.packTextBlockData(text=text_styles.main(item.getDescription()), padding=formatters.packPadding(14)))
        items.append(formatters.packBuildUpBlockData(topBlock))
        block = []
        block.append(formatters.packTextParameterBlockData(name=text_styles.stats(i18n.makeString('#tooltips:crewSkins/noSound')), value=text_styles.main(i18n.makeString('#tooltips:crewSkins/sound')), valueWidth=115))
        block.append(formatters.packTextParameterBlockData(name=text_styles.stats(str(len(item.getTankmenIDs()))), value=text_styles.main(i18n.makeString('#crew_skins:feature/inUse')), valueWidth=115))
        block.append(formatters.packTextParameterBlockData(name=text_styles.stats('{free}({max})'.format(free=item.getFreeCount(), max=item.getMaxCount())), value=text_styles.main(i18n.makeString('#crew_skins:feature/inStorage')), valueWidth=115))
        restrictions = []
        if item.getRoleID() is not None:
            restrictions.append(i18n.makeString(ITEM_TYPES.tankman_roles(item.getRoleID())))
        if item.getSex() in TANKMAN_SEX.ALL:
            restrictions.append(i18n.makeString(GenderRestrictionsLocals.LOCALES[item.getSex()]))
        if item.getNation() is not None:
            restrictions.append(i18n.makeString(NATIONS.all(item.getNation())))
        if restrictions:
            restrictionText = ', '.join(restrictions)
        else:
            restrictionText = i18n.makeString('#tooltips:crewSkins/noRestrictions')
        block.append(formatters.packTextParameterBlockData(name=text_styles.stats(restrictionText), value=text_styles.main(i18n.makeString('#tooltips:crewSkins/restrictions')), valueWidth=115))
        items.append(formatters.packBuildUpBlockData(block))
        skinUsersRoleAndVehicle = _skinUsersRoleAndVehicleText('{role} ({vehicle})', item)
        if skinUsersRoleAndVehicle:
            usedBlock = []
            usedBlock.append(formatters.packTextBlockData(text=text_styles.middleTitle(i18n.makeString('#tooltips:crewSkins/inUse'))))
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
        skinTankmanContext = self.context.buildItem(*args, **kwargs)
        topBlock = []
        topBlock.append(formatters.packTextBlockData(text=text_styles.middleTitle(i18n.makeString('#tooltips:crewSkins/allUsedHeader'))))
        topBlock.append(formatters.packTextBlockData(text=text_styles.main(i18n.makeString('#tooltips:crewSkins/allUsedDescr'))))
        items.append(formatters.packBuildUpBlockData(topBlock))
        skinUsersRoleAndVehicle = _skinUsersRoleAndVehicleText('{role} ({vehicle})', skinTankmanContext.crewSkin)
        usedBlock = []
        usedBlock.append(formatters.packTextBlockData(text=text_styles.middleTitle(i18n.makeString('#tooltips:crewSkins/inUse'))))
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
        block.append(formatters.packTextBlockData(text=text_styles.middleTitle('#tooltips:crewSkins/restrictions/header')))
        block.append(formatters.packTextBlockData(text=text_styles.main(i18n.makeString('#tooltips:crewSkins/restrictions'))))
        if crewSkin.getRoleID() is not None:
            text = i18n.makeString(ITEM_TYPES.tankman_roles(crewSkin.getRoleID()))
            highlight = text_styles.alert(text) if crewSkin.getRoleID() != tankman.role else text_styles.main(text)
            block.append(formatters.packTextBlockData(text=u'\u2022 ' + highlight))
        if crewSkin.getSex() in TANKMAN_SEX.ALL:
            text = i18n.makeString(GenderRestrictionsLocals.LOCALES[skinTankmanContext.crewSkin.getSex()])
            isTankmanAndSkinMale = crewSkin.getSex() == TANKMAN_SEX.MALE and not tankman.isFemale
            isTankmanAndSkinFemale = crewSkin.getSex() == TANKMAN_SEX.FEMALE and tankman.isFemale
            if isTankmanAndSkinMale or isTankmanAndSkinFemale:
                highlight = text_styles.main(text)
            else:
                highlight = text_styles.alert(text)
            block.append(formatters.packTextBlockData(text=u'\u2022 ' + highlight))
        if crewSkin.getNation() is not None:
            text = i18n.makeString(NATIONS.all(skinTankmanContext.crewSkin.getNation()))
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
        topBlock = []
        topBlock.append(formatters.packTextBlockData(text=text_styles.middleTitle('#tooltips:crewSkins/sound')))
        topBlock.append(formatters.packTextBlockData(text=text_styles.main('#tooltips:crewSkins/soundHeader')))
        topBlock.append(formatters.packImageTextBlockData(img=RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON, imgPadding={'left': -3,
         'top': -2}, txtOffset=20, padding=formatters.packPadding(bottom=0, top=8, left=0), desc=text_styles.alert('#tooltips:crewSkins/soundWarningDescr1')))
        items.append(formatters.packBuildUpBlockData(topBlock))
        infoBlock = []
        infoBlock.append(formatters.packImageTextBlockData(img=RES_ICONS.MAPS_ICONS_LIBRARY_INFO, imgPadding={'left': -3,
         'top': -2}, txtOffset=20, desc=text_styles.stats('!Available only for commander')))
        infoBlock.append(formatters.packTextBlockData(text=text_styles.main('!Push to heard this sound.'), padding=formatters.packPadding(left=20)))
        items.append(formatters.packBuildUpBlockData(infoBlock))
        return items
