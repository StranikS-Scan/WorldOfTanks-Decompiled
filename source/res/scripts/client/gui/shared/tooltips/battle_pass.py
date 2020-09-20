# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/battle_pass.py
from battle_pass_common import BATTLE_PASS_TOKEN_NEW_DEVICE_GIFT_OFFER, BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData

class DeviceGiftTokenTooltipData(BlocksTooltipData):
    TOKEN_TO_SHORT_NAME = {BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER: 'trophyGiftToken',
     BATTLE_PASS_TOKEN_NEW_DEVICE_GIFT_OFFER: 'newDeviceGiftToken'}

    def __init__(self, context):
        super(DeviceGiftTokenTooltipData, self).__init__(context, TOOLTIP_TYPE.DEVICE_GIFT_TOKEN)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(420)

    def _packBlocks(self, tokenID, **kwargs):
        deviceNames = self.context.buildItem(tokenID, **kwargs)
        isChooseDeviceEnabled = self.context.getParams().get('isChooseDeviceEnabled', True)
        shortName = self.TOKEN_TO_SHORT_NAME.get(tokenID, '')
        items = [formatters.packBuildUpBlockData(blocks=[self.__packTitleBlock(shortName), self.__packImageBlock(tokenID)], padding=formatters.packPadding(bottom=-28)), self.__packDeviceNameBlocks(shortName, deviceNames, isChooseDeviceEnabled)]
        return items

    @staticmethod
    def __packTitleBlock(shortName):
        return formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.tooltips.battlePassDeviceOffer.title.dyn(shortName)())))

    @staticmethod
    def __packImageBlock(tokenID):
        if tokenID == BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER:
            image = R.images.gui.maps.icons.battlePass2020.tooltips.trophyDevices()
        else:
            image = R.images.gui.maps.icons.battlePass2020.tooltips.standardDevices()
        return formatters.packImageBlockData(img=backport.image(image), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-28))

    @staticmethod
    def __packDeviceNameBlocks(shortName, trophyNames, isChooseDeviceEnabled):
        if isChooseDeviceEnabled:
            blocks = [ formatters.packTextBlockData(text=text_styles.main(trophyName)) for trophyName in trophyNames ]
        else:
            blocks = [formatters.packImageTextBlockData(title=text_styles.main(backport.text(R.strings.tooltips.battlePassDeviceOffer.error.dyn(shortName)())), img=backport.image(R.images.gui.maps.icons.library.alertIcon1()))]
        blocks.append(formatters.packTextBlockData(text=text_styles.standard(backport.text(R.strings.tooltips.battlePassDeviceOffer.footer.dyn(shortName)())), padding=formatters.packPadding(top=8)))
        return formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(left=-1), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)
