# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/tooltips/event.py
from __future__ import absolute_import
from constants import FORCE_FINITE_SHELL_TAG
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.shared.items_parameters import params_helper
from gui.shared.tooltips import formatters
from gui.shared.tooltips.vehicle import VehicleInfoTooltipData, StatusBlockConstructor, HeaderBlockConstructor, SimplifiedStatsBlockConstructor
from gui.shared.tooltips.module import ModuleBlockTooltipData, EffectsBlockConstructor, HeaderBlockConstructor as ModuleHeaderBlockConstructor
from gui.shared.tooltips.shell import ShellBlockToolTipData, CommonStatsBlockConstructor
from halloween.gui.scaleform.genConsts.HALLOWEEN_ICON_TEXT_FRAMES import HALLOWEEN_ICON_TEXT_FRAMES
from halloween.gui.scaleform.genConsts.HALLOWEEN_BLOCKS_TOOLTIP_TYPES import HALLOWEEN_BLOCKS_TOOLTIP_TYPES
from halloween.gui.impl.gen.view_models.views.lobby.widgets.hangar_carousel_vehicle_view_model import VehicleStates
from halloween.gui.impl.lobby.hw_helpers import isDailyKeyQuestCompleted, getVehicleState
from gui.shared.tooltips.shell import HeaderBlockConstructor as ShellHeaderBlockConstructor
_TOOLTIP_MIN_WIDTH = 380

class EventVehicleInfoTooltipData(VehicleInfoTooltipData, IGlobalListener):

    def _getCrewIconBlock(self):
        tImg = RES_ICONS.MAPS_ICONS_MESSENGER_ICONCONTACTS
        return [formatters.packImageBlockData(img=tImg, alpha=0)]

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        isShort = self.context.getParams().get('isShort', False)
        items = []
        vehicle = self.item
        statsConfig = self.context.getStatsConfiguration(vehicle)
        paramsConfig = self.context.getParamsConfiguration(vehicle)
        statusConfig = self.context.getStatusConfiguration(vehicle)
        leftPadding = self._LEFT_PADDING
        rightPadding = self._RIGHT_PADDING
        bottomPadding = 12
        blockTopPadding = -4
        leftRightPadding = formatters.packPadding(left=leftPadding, right=rightPadding)
        blockPadding = formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding)
        valueWidth = 77
        headerItems = [formatters.packBuildUpBlockData(EventHeaderBlockConstructor(vehicle, statsConfig, leftPadding, rightPadding).construct(), padding=leftRightPadding, blockWidth=410), formatters.packBuildUpBlockData(self._getCrewIconBlock(), gap=2, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT, padding=formatters.packPadding(top=34, right=0), blockWidth=20)]
        headerBlockItems = [formatters.packBuildUpBlockData(headerItems, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(bottom=-16))]
        if not isDailyKeyQuestCompleted(vehicle.intCD) and not isShort:
            headerBlockItems.append(formatters.packTextParameterWithIconBlockData(linkage=HALLOWEEN_BLOCKS_TOOLTIP_TYPES.HALLOWEEN_TOOLTIP_TEXT_PARAMETER_WITH_ICON_BLOCK_LINKAGE, name=text_styles.main(backport.text(R.strings.halloween_tooltips.vehicle.eventBonus())), value='', icon=HALLOWEEN_ICON_TEXT_FRAMES.HW_EVENT_KEY, iconYOffset=-2, valueWidth=valueWidth - 8, nameOffset=8, gap=0, padding=formatters.packPadding(left=2, top=3, bottom=3)))
        items.append(formatters.packBuildUpBlockData(headerBlockItems, gap=-4, padding=formatters.packPadding(bottom=-12)))
        simplifiedStatsBlock = SimplifiedStatsBlockConstructor(vehicle, paramsConfig, leftPadding, rightPadding).construct()
        if simplifiedStatsBlock:
            items.append(formatters.packBuildUpBlockData(simplifiedStatsBlock, gap=-4, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=leftRightPadding))
        if not vehicle.isRotationGroupLocked and not isShort:
            statusBlock, operationError, _ = EventStatusBlockConstructor(vehicle, statusConfig).construct()
            if statusBlock and not operationError:
                items.append(formatters.packBuildUpBlockData(statusBlock, padding=blockPadding, blockWidth=440))
            else:
                self._setContentMargin(bottom=bottomPadding)
        return items


class EventStatusBlockConstructor(StatusBlockConstructor):

    def construct(self):
        state = getVehicleState(self.vehicle)
        if state.value == VehicleStates.LOCKED.value:
            return ([formatters.packAlignedTextBlockData(text_styles.statusAlert(backport.text(R.strings.halloween_tooltips.vehicle.state.locked.title())), BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)], None, None)
        elif state.value == VehicleStates.INPLATOON.value:
            return ([formatters.packAlignedTextBlockData(text_styles.statusAttention(backport.text(R.strings.halloween_lobby.carousel.card.inPlatoon())), BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)], None, None)
        else:
            return ([formatters.packAlignedTextBlockData(text_styles.critical(backport.text(R.strings.halloween_lobby.carousel.card.inBattle())), BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)], None, None) if state.value == VehicleStates.INBATTLE.value else super(EventStatusBlockConstructor, self).construct()


class EventHeaderBlockConstructor(HeaderBlockConstructor):

    def construct(self):
        block = []
        headerBlocks = []
        nameStr = text_styles.highTitle(self.vehicle.userName)
        icon = getTypeBigIconPath(self.vehicle.type, False)
        headerBlocks.append(formatters.packImageTextBlockData(title=nameStr, desc='', img=icon, imgPadding=formatters.packPadding(left=10, top=-15), txtGap=-9, txtOffset=99, padding=formatters.packPadding(top=15, bottom=-15 if self.vehicle.isFavorite else -21)))
        headerBlocks.append(formatters.packTextBlockData(text_styles.main(self.vehicle.longDescriptionSpecial), padding=formatters.packPadding(top=-28, left=99, bottom=9)))
        block.append(formatters.packBuildUpBlockData(headerBlocks, stretchBg=False, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_NORMAL_VEHICLE_BG_LINKAGE, padding=formatters.packPadding(left=-self.leftPadding)))
        return block


class EventModuleBlockTooltipData(ModuleBlockTooltipData):

    def _getHeaderBlockConstructor(self):
        return EventModuleHeaderBlockConstructor

    def _getEffectsBlockConstructor(self):
        return EventEffectsBlockConstructor


class EventModuleHeaderBlockConstructor(ModuleHeaderBlockConstructor):

    def _getCooldownSeconds(self):
        vehicle = self.configuration.vehicle
        descr = self.module.descriptor
        variant = descr.getVariant(vehicle.descriptor) if vehicle else descr.fallbackVariant
        return variant.cooldownSeconds


class EventEffectsBlockConstructor(EffectsBlockConstructor):

    def _getOnUseStr(self, attribs, isRemovingStun, **kpiArgs):
        vehicle = self.configuration.vehicle
        descr = self.module.descriptor
        variant = descr.getVariant(vehicle.descriptor) if vehicle else descr.fallbackVariant
        base = super(EventEffectsBlockConstructor, self)._getOnUseStr(attribs, isRemovingStun, **kpiArgs)
        usageCostStr = backport.text(attribs.dyn('usageCost', R.strings.artefacts.hwAbility.usageCost.default)())
        return makeHtmlString('html_templates:lobby/hangar', 'abilityUsageCost', ctx={'onUse': base,
         'usageCostStr': usageCostStr,
         'cost': variant.usageCost})


class EventShellBlockToolTipData(ShellBlockToolTipData):

    def _packBlocks(self, *args, **kwargs):
        self._setContentMargin(top=0, left=17, bottom=20, right=0)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_MIN_WIDTH)
        self.item = self.context.buildItem(*args, **kwargs)
        items = []
        shell = self.item
        statsConfig = self.context.getStatsConfiguration(shell)
        paramsConfig = self.context.getParamsConfiguration(shell)
        valueWidth = 107
        leftPadding = 0
        rightPadding = 20
        lrPaddings = formatters.packPadding(left=leftPadding, right=rightPadding)
        blockTopPadding = -4
        bottomPadding = -5
        blockPadding = formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding, bottom=bottomPadding)
        textGap = -2
        vDescr = paramsConfig.vehicle.descriptor if paramsConfig.vehicle is not None else None
        params = params_helper.getParameters(shell, vDescr)
        items.append(formatters.packBuildUpBlockData(ShellHeaderBlockConstructor(shell, statsConfig, leftPadding, rightPadding, params).construct(), padding=formatters.packPadding(left=17, right=rightPadding, top=14)))
        statsBlock = CommonStatsBlockConstructor(shell, paramsConfig, valueWidth, mechanic=None, params=params).construct()
        if statsBlock:
            items.append(formatters.packBuildUpBlockData(statsBlock, padding=blockPadding, gap=textGap))
        if statsConfig.showCompatibles:
            moduleCompatibles = params_helper.getCompatibles(shell)
            compatibleBlocks = []
            for paramType, paramValue in moduleCompatibles:
                compatibleBlocks.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.menu.moduleInfo.compatible.dyn(paramType)())), desc=text_styles.main(paramValue)))

            compatibleBlocks.append(formatters.packTextBlockData(text=text_styles.stats(backport.text(R.strings.menu.moduleInfo.additionalInfo()))))
            if compatibleBlocks:
                items.append(formatters.packBuildUpBlockData(compatibleBlocks, padding=formatters.packPadding(left=leftPadding, bottom=8)))
        if params.get('isBasic'):
            boldText = text_styles.stats(backport.text(R.strings.tooltips.shell.basic.description.bold()))
            items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.standard(backport.text(R.strings.tooltips.shell.basic.description(), bold=boldText)), padding=lrPaddings)], padding=formatters.packPadding(right=rightPadding)))
        if FORCE_FINITE_SHELL_TAG in self.item.descriptor.tags:
            boldText = text_styles.neutral(backport.text(R.strings.tooltips.hwShell.alt.description.bold()))
            items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.standard(backport.text(R.strings.tooltips.hwShell.alt.description(), bold=boldText)), padding=lrPaddings)], padding=formatters.packPadding(right=rightPadding)))
        return items
