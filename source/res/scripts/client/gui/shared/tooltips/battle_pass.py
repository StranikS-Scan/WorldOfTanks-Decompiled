# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/battle_pass.py
from battle_pass_common import BattlePassState
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IBattlePassController

class BattlePassGiftTokenTooltipData(BlocksTooltipData):
    _MAX_GIFTS_COUNT = 12

    def __init__(self, context):
        super(BattlePassGiftTokenTooltipData, self).__init__(context, TOOLTIP_TYPE.BATTLE_PASS_GIFT_TOKEN)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(420)

    def _packBlocks(self, tokenID, isReceived=False, **kwargs):
        giftsNames = self.context.buildItem(tokenID, **kwargs)
        isOfferEnabled = self.context.getParams().get('isOfferEnabled', True)
        shortName = tokenID.split(':')[2]
        items = [self.__packImageBlock(shortName), self.__packGiftNameBlocks(shortName, giftsNames, isOfferEnabled)]
        if not isReceived:
            items.append(self.__packFooterBlock(shortName))
        return items

    @staticmethod
    def __packFooterBlock(shortName):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.standard(backport.text(R.strings.tooltips.battlePassOffer.footer.dyn(shortName)())), padding=formatters.packPadding(top=8))], padding=formatters.packPadding(left=-1))

    @staticmethod
    def __packImageBlock(shortName):
        image = R.images.gui.maps.icons.battlePass.tooltips.dyn(shortName)
        if not image.exists():
            image = R.images.gui.maps.icons.battlePass.tooltips.new_device_fv_gift
        return formatters.packImageBlockData(img=backport.image(image()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-1))

    @classmethod
    def __packGiftNameBlocks(cls, shortName, giftsNames, isOfferEnabled):
        rOffer = R.strings.tooltips.battlePassOffer
        blocks = [formatters.packTextBlockData(text=text_styles.highTitle(backport.text(rOffer.title.dyn(shortName)())))]
        if isOfferEnabled:
            if shortName in ('brochure_gift', 'guide_gift', 'blueprint_gift', 'book_gift'):
                blocks.append(formatters.packTextBlockData(text=text_styles.gold(backport.text(rOffer.allNations()))))
                if shortName == 'blueprint_gift':
                    information = backport.text(rOffer.blueprintInfo())
                else:
                    experience = first(giftsNames)
                    experienceText = text_styles.expText(backport.getIntegralFormat(experience))
                    information = backport.text(rOffer.crewBookInfo(), exp=experienceText)
                blocks.append(formatters.packTextBlockData(text=text_styles.main(information)))
            else:
                insertEtc = False
                if len(giftsNames) > cls._MAX_GIFTS_COUNT:
                    giftsNames = giftsNames[:cls._MAX_GIFTS_COUNT - 1]
                    insertEtc = True
                for gift in giftsNames:
                    giftName = backport.text(rOffer.point(), item=gift)
                    blocks.append(formatters.packTextBlockData(text=text_styles.main(giftName)))

                if insertEtc:
                    blocks.append(formatters.packTextBlockData(text=text_styles.stats(backport.text(rOffer.etc()))))
        else:
            blocks.append(formatters.packImageTextBlockData(title=text_styles.main(backport.text(rOffer.error())), img=backport.image(R.images.gui.maps.icons.library.alertIcon1())))
        return formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(left=-1), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)


class BattlePassPointsTooltipData(BlocksTooltipData):
    __battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self, context):
        super(BattlePassPointsTooltipData, self).__init__(context, TOOLTIP_TYPE.BATTLE_PASS_POINTS)
        self._setWidth(360)

    def _packBlocks(self, *args, **kwargs):
        self._items = super(BattlePassPointsTooltipData, self)._packBlocks(*args, **kwargs)
        titleBlock = formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.battle_pass.tooltips.battlePassPoints.title())))
        imageBlock = formatters.packImageBlockData(img=backport.image(R.images.gui.maps.icons.battlePass.tooltips.battlePassPoints()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
        titleImageBlock = formatters.packBuildUpBlockData([titleBlock, imageBlock])
        self._items.append(titleImageBlock)
        descriptionBlock = text_styles.main(backport.text(R.strings.battle_pass.tooltips.battlePassPoints.description()))
        self._items.append(formatters.packTextBlockData(descriptionBlock))
        state = self.__battlePassController.getState()
        if state == BattlePassState.COMPLETED:
            self._items.append(formatters.packBuildUpBlockData([formatters.packImageTextBlockData(title=text_styles.success(backport.text(R.strings.battle_pass.tooltips.battlePassPoints.completed())), img=backport.image(R.images.gui.maps.icons.library.check()), imgPadding=formatters.packPadding(top=-2))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(bottom=-10)))
        return self._items
