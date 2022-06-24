# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/tooltips/instruction.py
from shared_utils import first
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import getOfferTokenByGift
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_COMPONENT, TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.contexts import ToolTipContext
from helpers import dependency
from skeletons.gui.offers import IOffersDataProvider

class EpicBattleTokenInstructionContext(ToolTipContext):
    __slots__ = ('__hasOffer',)
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self):
        super(EpicBattleTokenInstructionContext, self).__init__(TOOLTIP_COMPONENT.EPIC_BATTLE)
        self.__hasOffer = True

    def buildItem(self, tokenID, **kwargs):
        self.__hasOffer = True
        result = []
        shortName = tokenID.split(':')[2]
        offerToken = getOfferTokenByGift(tokenID)
        offer = self.__offersProvider.getOfferByToken(offerToken)
        if offer is None:
            self.__hasOffer = False
            return result
        else:
            if shortName in 'brochure_gift':
                gift = first(offer.getAllGifts())
                if gift is not None:
                    result.append(gift.bonus.displayedItem.getXP())
            else:
                for gift in offer.getAllGifts():
                    result.append(gift.title)

                result = sorted(result)
            return result


class EpicBattleInstructionTooltipData(BlocksTooltipData):
    _MAX_GIFTS_COUNT = 12

    def __init__(self, context):
        super(EpicBattleInstructionTooltipData, self).__init__(context, TOOLTIP_TYPE.EPIC_BATTLE_GIFT_TOKEN)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(420)

    def _packBlocks(self, tokenID, **kwargs):
        giftsNames = self.context.buildItem(tokenID, **kwargs)
        shortName = tokenID.split(':')[2]
        items = [self.__packImageBlock(shortName), self.__packGiftNameBlocks(shortName, giftsNames)]
        return items

    @staticmethod
    def __packImageBlock(shortName):
        image = R.images.gui.maps.icons.epicBattles.tooltips.dyn(shortName)
        return formatters.packImageBlockData(img=backport.image(image()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-1))

    @classmethod
    def __packGiftNameBlocks(cls, shortName, giftsNames):
        rOffer = R.strings.tooltips.epicBattlesOffer
        blocks = [formatters.packTextBlockData(text=text_styles.highTitle(backport.text(rOffer.title.dyn(shortName)())))]
        if shortName == 'brochure_gift':
            blocks.append(formatters.packTextBlockData(text=text_styles.gold(backport.text(rOffer.allNations()))))
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
        return formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(left=-1), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)
