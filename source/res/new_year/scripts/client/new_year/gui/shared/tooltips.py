# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/shared/tooltips.py
import BigWorld
from dog_tags_common.components_config import componentConfigAdapter as cca
from dog_tags_common.number_formatter import formatComponentValue
from dog_tags_common.player_dog_tag import PlayerDogTag
from gui.dog_tag_composer import AssetSize
from gui.impl import backport
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import ToolTipBaseData, TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.dog_tags import DogTagInfoTooltip
from new_year.gui.impl.lobby.new_year.tooltips.ny_total_bonus_tooltip import NyTotalBonusTooltip
from helpers import getLanguageCode

class NYCreditBonusTooltipWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(NYCreditBonusTooltipWindowData, self).__init__(context, TOOLTIP_TYPE.NY_CREDIT_BONUS)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(NyTotalBonusTooltip(), useDecorator=False)


class NewYearFillers(BlocksTooltipData):

    def __init__(self, context):
        super(NewYearFillers, self).__init__(context, None)
        self._setWidth(365)
        self._setContentMargin(0, 0, 0, 0)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(NewYearFillers, self)._packBlocks(*args, **kwargs)
        blocks = [formatters.packImageBlockData(backport.image(R.images.new_year.gui.maps.icons.newYear.infotype.icon_filler())), formatters.packTextBlockData(text_styles.highTitle(backport.text(R.strings.ny.fillersTooltip.header())), padding=formatters.packPadding(-364, 30, 0, 30)), formatters.packTextBlockData(text_styles.mainBig(backport.text(R.strings.ny.fillersTooltip.description())), padding=formatters.packPadding(240, 30, 30, 30))]
        items.append(formatters.packBuildUpBlockData(blocks=blocks))
        return items


class NyStaticDogTagInfoTooltip(DogTagInfoTooltip):

    def _packBlocks(self, compId, top, userID=None):
        items = []
        comp = cca.getComponentById(compId)
        if userID is None:
            componentProgress = BigWorld.player().dogTags.getComponentProgress(compId)
        else:
            dogTag = PlayerDogTag.fromDict(self.itemsCache.items.getDogTag(int(userID)))
            componentProgress = dogTag.getComponentByType(comp.viewType)
        items.append(formatters.packTextBlockData(text_styles.middleTitle(backport.text(R.strings.ny.dogTag.header.static())), padding=self._titlePadding))
        typeLevelBlock = [text_styles.main(backport.text(R.strings.ny.dogTag.tab.static()))]
        items.append(formatters.packTextBlockData(text_styles.concatStylesToSingleLine(*typeLevelBlock), padding=self._levelPadding))
        playerPos = componentProgress.value
        if playerPos:
            valueBlock = list()
            valueBlock.append(text_styles.main('{} '.format(backport.text(R.strings.ny.dogTag.top.place()))))
            statStr = formatComponentValue(getLanguageCode(), playerPos, comp.numberType, specialReplacements=False)
            valueBlock.append(text_styles.neutral(statStr))
            items.append(formatters.packTextBlockData(text_styles.concatStylesToSingleLine(*valueBlock)))
        imageRes = R.images.new_year.gui.maps.icons.newYear.common.rewards.dogtags.s200x150.dyn('dogtag_' + str(top))
        if not imageRes.exists():
            imageRes = backport.image(R.images.gui.maps.icons.dogtags.dyn(AssetSize.SMALL.value).backgrounds.background_66_0())
        items.append(formatters.packImageBlockData(backport.image(imageRes()), padding=formatters.packPadding(top=self._imagePaddingTop, bottom=self._imagePaddingBottom)))
        items.append(formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.ny.dogTag.top.description.common())), padding=self._descriptionPadding))
        return [formatters.packBuildUpBlockData(blocks=items)]
