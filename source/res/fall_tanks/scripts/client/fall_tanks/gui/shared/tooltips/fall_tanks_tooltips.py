# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/shared/tooltips/fall_tanks_tooltips.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.formatters import packTextBlockData
from gui.shared.tooltips.module import ModuleTooltipBlockConstructor
from gui.shared.tooltips import formatters
from gui.shared.items_parameters import params_helper
from gui.shared.items_parameters import formatters as params_formatters
from fall_tanks.gui.fall_tanks_gui_constants import FALL_TANKS_IMAGES_PATH
_IMAGE_LEFT_PADDING = 69

class FallTanksBlockToolTipData(BlocksTooltipData):

    def __init__(self, context, toolTipType):
        super(FallTanksBlockToolTipData, self).__init__(context, toolTipType)
        self._setWidth(360)
        self._setContentMargin(top=20, left=21, bottom=20, right=21)


class FallTanksShellBlockToolTipData(FallTanksBlockToolTipData):

    def _packBlocks(self, *args, **kwargs):
        shell = self.context.buildItem(*args, **kwargs)
        caliberName = ModuleTooltipBlockConstructor.CALIBER
        params = params_helper.getParameters(shell)
        caliberValue = dict(params_formatters.getFormattedParamsList(shell.descriptor, params)).get(caliberName)
        headerTextBlock = formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.fall_tanks.shellTooltip.header())), desc=params_formatters.formatParamNameColonValueUnits(caliberName, caliberValue), descPadding=formatters.packPadding(top=10), gap=-5)
        shellImageBlock = formatters.packImageBlockData(img=backport.image(FALL_TANKS_IMAGES_PATH.shells.shell_tooltip()), padding=formatters.packPadding(left=_IMAGE_LEFT_PADDING))
        descriptionBlock = packTextBlockData(text_styles.main(backport.text(R.strings.fall_tanks.shellTooltip.description())), padding=formatters.packPadding(top=-5))
        return [formatters.packBuildUpBlockData([headerTextBlock, shellImageBlock]), descriptionBlock]


class FallTanksAbilitiesBlockToolTipData(FallTanksBlockToolTipData):

    def _packBlocks(self, *args, **kwargs):
        item = self.context.buildItem(*args, **kwargs)
        descriptor = item.descriptor
        abilityNameBlock = packTextBlockData(text_styles.highTitle(item.shortUserName), padding=formatters.packPadding(top=-10))
        cooldownTimeBlock = packTextBlockData(params_formatters.formatParamNameColonValueUnits(paramName=ModuleTooltipBlockConstructor.COOLDOWN_SECONDS, paramValue=backport.getNiceNumberFormat(descriptor.cooldownSeconds)))
        typeNameBlock = formatters.packTextBlockData(text_styles.main(backport.text(R.strings.fall_tanks.ability.name())))
        imageBlock = formatters.packImageBlockData(img=backport.image(FALL_TANKS_IMAGES_PATH.consumables.tooltips.dyn(descriptor.icon[0])()), padding=formatters.packPadding(left=_IMAGE_LEFT_PADDING))
        descriptionBlock = packTextBlockData(text_styles.main(descriptor.description), padding=formatters.packPadding(top=-5))
        return [formatters.packBuildUpBlockData([abilityNameBlock,
          typeNameBlock,
          cooldownTimeBlock,
          imageBlock]), descriptionBlock]
