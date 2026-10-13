# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/advanced/__init__.py
import typing
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen_utils import DynAccessor
from gui.shared.formatters import text_styles
from gui.shared.gui_items.fitting_item import FittingItem
from gui.shared.tooltips import formatters
from gui.shared.tooltips.advanced.data.battle_booster_alt_key_data import BattleBoosterKeyData
from gui.shared.tooltips.advanced.data.chassis_alt_key_data import ChassisAltKeyData
from gui.shared.tooltips.advanced.data.default_alt_key_data import AltKeyData
from gui.shared.tooltips.advanced.data.default_alt_key_data import DefaultAltKeyData
from gui.shared.tooltips.advanced.data.equipment_alt_key_data import EquipmentAltKeyData
from gui.shared.tooltips.advanced.data.gun_alt_key_data import GunAltKeyData
from gui.shared.tooltips.advanced.data.optional_device_alt_key_data import OptionalDeviceAltKeyData
from gui.shared.tooltips.advanced.data.shell_alt_key_data import ShellKeyData
from gui.shared.tooltips.advanced.data.turret_alt_key_data import TurretAltKeyData
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.complex_formatters import doAdvancedCounterText
if typing.TYPE_CHECKING:
    from typing import Any, Optional, Tuple, Union

class BaseAdvancedTooltip(BlocksTooltipData):
    _ADVANCED_ANIM_PATH_PATTERN = 'animations/advancedHints/{}.swf'

    def __init__(self, context):
        super(BaseAdvancedTooltip, self).__init__(context, None)
        self._setContentMargin(top=2, left=3, bottom=3, right=3)
        self._setMargins(afterBlock=0)
        self._setWidth(415)
        self._item = None
        return

    def buildToolTip(self, *args, **kwargs):
        self._item = self.context.buildItem(*args, **kwargs)
        return super(BaseAdvancedTooltip, self).buildToolTip(*args, **kwargs)

    def getDisplayableData(self, *args, **kwargs):
        multipleDataVO = []
        tooltipsData = self._getTooltipData(*args, **kwargs)
        countTooltips = len(tooltipsData)
        for idx, itemData in enumerate(tooltipsData):
            blocks = self._packAdvancedBlocks(itemData.swfName, itemData.header, itemData.description, idx, countTooltips)
            multipleDataVO.append(self._packTooltipVO(blocks))

        return multipleDataVO

    @staticmethod
    def getMovieAnimationPath(sfwName):
        return BaseAdvancedTooltip._ADVANCED_ANIM_PATH_PATTERN.format(sfwName)

    def _getTooltipData(self, *args, **kwargs):
        pass

    def _packAdvancedBlocks(self, swfName, header, description, idx=0, count=0):
        descrText = self.__formatDescription(description)
        if swfName:
            items = self.__packSwfBlocks(swfName, header, descrText, idx, count)
        else:
            items = self.__packBlocksWithoutSwf(header, descrText)
        return items

    def __formatDescription(self, description):
        descrText = ''
        if isinstance(description, (str, unicode)):
            descrTextR = R.strings.tooltips.advanced.dyn(description)
            if descrTextR and descrTextR.isValid():
                descrText = backport.text(descrTextR())
            else:
                descrText = description
        elif isinstance(description, DynAccessor) and description.isValid():
            backport.text(description())
        return descrText

    def __packBlocksWithoutSwf(self, header, descrText):
        return [formatters.packTextBlockData(text=text_styles.highTitle(header), padding=formatters.packPadding(left=20, top=20)), formatters.packTextBlockData(text=text_styles.main(descrText), padding=formatters.packPadding(left=20, top=10, bottom=20))]

    def __packSwfBlocks(self, swfName, header, descrText, idx, count):
        blocks = [formatters.packTextBlockData(text=text_styles.highTitle(header), padding=formatters.packPadding(left=20, top=20)), formatters.packImageBlockData(BaseAdvancedTooltip.getMovieAnimationPath(swfName), BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=5, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_ADVANCED_CLIP_BLOCK_LINKAGE)]
        textTopPadding = 10
        if count > 1:
            textTopPadding = -10
            text = backport.text(R.strings.tooltips.advanced.shuffle.counter(), idx=idx + 1, count=count)
            blocks.append(formatters.packTextBlockData(text=doAdvancedCounterText(text), padding=formatters.packPadding(top=-12)))
        blocks.append(formatters.packTextBlockData(text=text_styles.main(descrText), padding=formatters.packPadding(left=20, top=textTopPadding, bottom=20)))
        return blocks


class ComplexAdvanced(BaseAdvancedTooltip):
    _COMPLEX_ADVANCED_HEADER_PATTERN = '#tooltips:advanced/{}/header'

    def _getTooltipData(self, item, *args, **kwargs):
        swfName, linkage = item
        headerKey = self._COMPLEX_ADVANCED_HEADER_PATTERN.format(swfName)
        if headerKey in TOOLTIPS.ADVANCED_ENUM:
            header = headerKey
        else:
            header = linkage + '/header'
        return (AltKeyData(swfName=swfName, header=header, description=swfName),)
