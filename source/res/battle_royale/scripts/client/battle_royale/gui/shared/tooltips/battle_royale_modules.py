# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/shared/tooltips/battle_royale_modules.py
from gui.Scaleform.daapi.view.common.battle_royale.params import getModuleParameters, getVehicleParameters
from gui.Scaleform.genConsts.ATLAS_CONSTANTS import ATLAS_CONSTANTS
from gui.doc_loaders.battle_royale_settings_loader import getTreeModuleIcon, getTreeModuleHeader
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
_TOOLTIP_MIN_WIDTH = 410

class BattleRoyaleModulesTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(BattleRoyaleModulesTooltip, self).__init__(context, TOOLTIP_TYPE.MODULE)
        self._setContentMargin(top=0, left=0, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        self.item, currentModule = self.context.buildItem(*args, **kwargs)
        items = super(BattleRoyaleModulesTooltip, self)._packBlocks()
        module = self.item
        if module is None:
            return []
        else:
            leftPadding = 20
            rightPadding = 20
            topPadding = 20
            textGap = -2
            headerBlock = HeaderBlockConstructor.construct(module)
            items.append(formatters.packBuildUpBlockData(headerBlock, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=topPadding)))
            paramsBlock = ParamsBlockConstructor.construct(module, currentModule, self._getVehicle())
            if paramsBlock:
                items.append(formatters.packBuildUpBlockData(paramsBlock, padding=formatters.packPadding(left=leftPadding, top=2), gap=textGap))
            return items

    def _getVehicle(self):
        return self.context.getVehicle()


class HeaderBlockConstructor(object):

    @classmethod
    def construct(cls, module):
        return cls.__constructVehicle(module) if module.itemTypeID == GUI_ITEM_TYPE.VEHICLE else cls.__constructModule(module)

    @classmethod
    def __constructModule(cls, module):
        block = []
        moduleDescr = module.descriptor
        icon = getTreeModuleIcon(module)
        if icon:
            block.append(formatters.packAtlasIconTextBlockData(title=text_styles.highTitle(getTreeModuleHeader(module)), desc=text_styles.standard(moduleDescr.userString), atlas=ATLAS_CONSTANTS.COMMON_BATTLE_LOBBY, icon=icon, iconPadding=formatters.packPadding(right=12), txtGap=1, txtPadding=formatters.packPadding(top=7)))
        return block

    @classmethod
    def __constructVehicle(cls, vehicle):
        block = []
        block.append(formatters.packAtlasIconTextBlockData(title=text_styles.highTitle(vehicle.userName), atlas=ATLAS_CONSTANTS.COMMON_BATTLE_LOBBY, icon='vehicle', iconPadding=formatters.packPadding(right=12), txtGap=1, txtPadding=formatters.packPadding(top=7)))
        return block


class ParamsBlockConstructor(object):

    @staticmethod
    def construct(module, currentModule, vehicle):
        block = []
        if module.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            params = getVehicleParameters(vehicle)
            leftPadding = -45
        else:
            params = getModuleParameters(module, vehicle, currentModule)
            leftPadding = 35
        for item in params:
            bottomPadding = 10 if item.get('isLastInGroup', False) else 0
            block.append(formatters.packTextParameterBlockData(name=item['description'], value=item['value'], valueWidth=110, padding=formatters.packPadding(left=leftPadding, bottom=bottomPadding)))

        return block
