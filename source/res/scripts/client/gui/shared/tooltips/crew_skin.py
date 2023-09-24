# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/crew_skin.py
from skeletons.gui.shared import IItemsCache
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.impl.gen import R
from gui.impl import backport
from helpers import dependency
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.gui_items.Tankman import getCrewSkinIconBig
from gui.shared.gui_items.crew_skin import localizedFullName, Rarity
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from items.components.crew_skins_constants import TANKMAN_SEX
from skeletons.gui.lobby_context import ILobbyContext
_MAX_USERS_DISPLAYED = 10

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _skinUsersRoleAndVehicleText(fstring, item, itemsCache=None):
    return [ fstring.format(role=backport.text(R.strings.item_types.tankman.roles.dyn(tankman.role)()), vehicle=itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr).shortUserName) for invID, tankman in itemsCache.items.getTankmen().iteritems() if invID in item.getTankmenIDs() ]


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
        topBlock.append(formatters.packImageTextBlockData(img=getCrewSkinIconBig(item.getIconID()), imgPadding=formatters.packPadding(left=60), padding=formatters.packPadding(-142)))
        topBlock.append(formatters.packTextBlockData(text=self.__stripUnsupportedFlashTags(text_styles.main(item.getDescription())), padding=formatters.packPadding(14)))
        items.append(formatters.packBuildUpBlockData(topBlock))
        block = []
        block.append(formatters.packTextParameterBlockData(name=text_styles.stats(str(len(item.getTankmenIDs()))), value=text_styles.main(backport.text(R.strings.crew_skins.feature.inUse())), valueWidth=115))
        block.append(formatters.packTextParameterBlockData(name=text_styles.stats(str(item.getFreeCount())), value=text_styles.main(backport.text(R.strings.crew_skins.feature.inStorage())), valueWidth=115))
        restrictions = []
        if item.getSex() == TANKMAN_SEX.MALE:
            restrictions.append(backport.text(R.strings.item_types.tankman.gender.man()))
        elif item.getSex() == TANKMAN_SEX.FEMALE:
            restrictions.append(backport.text(R.strings.item_types.tankman.gender.woman()))
        if item.getNation() is not None:
            restrictions.append(backport.text(R.strings.nations.dyn(item.getNation())()))
        if restrictions:
            restrictionText = ', '.join(restrictions)
        else:
            restrictionText = backport.text(R.strings.tooltips.crewSkins.noRestrictions())
        block.append(formatters.packTextParameterBlockData(name=text_styles.stats(restrictionText), value=text_styles.main(backport.text(R.strings.tooltips.crewSkins.restrictions())), valueWidth=115))
        items.append(formatters.packBuildUpBlockData(block))
        skinUsersRoleAndVehicle = _skinUsersRoleAndVehicleText('{role} ({vehicle})', item)
        if skinUsersRoleAndVehicle:
            usedBlock = []
            usedBlock.append(formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.crewSkins.inUse()))))
            usedBlock.append(formatters.packTextBlockData(text=text_styles.main(_longStringListEllipsisCutoff(', ', skinUsersRoleAndVehicle, _MAX_USERS_DISPLAYED))))
            items.append(formatters.packBuildUpBlockData(usedBlock))
        return items

    @staticmethod
    def __stripUnsupportedFlashTags(text):
        return text.replace('&zwnbsp;', '')
