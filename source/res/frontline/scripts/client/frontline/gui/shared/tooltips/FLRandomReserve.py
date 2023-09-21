# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/shared/tooltips/FLRandomReserve.py
import BigWorld
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, i18n
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IEpicBattleMetaGameController

class FLRandomReserve(BlocksTooltipData):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _NO_STACK_TOOLTIP_MIN_WIDTH = 315
    _STACK_TOOLTIP_MIN_WIDTH = 282
    _DISABLED_TOOLTIP_MIN_WIDTH = 244
    _RESERVES_OFFSET = 6
    USED_SLOT = 0

    def __init__(self, context):
        super(FLRandomReserve, self).__init__(context, TOOLTIP_TYPE.EQUIPMENT)
        self.itemCD = None
        self._setContentMargin(top=16, left=21, bottom=5, right=0)
        return

    def _packBlocks(self, *args, **kwargs):
        item = self.context.buildItem(*args, **kwargs)
        if self.__isUsed(item):
            self._setWidth(self._DISABLED_TOOLTIP_MIN_WIDTH)
            return self.__getDisabledBlocks()
        self.itemCD = item.getDescriptor().compactDescr
        equipment = self.__getEquipmentByIntCD(self.itemCD)
        isStack = self.__epicController.isReserveStack(equipment.extraName())
        hasRandomBonusCap = self.__epicController.hasBonusCap(ARENA_BONUS_TYPE_CAPS.EPIC_RANDOM_RESERVES)
        index = args[0]
        width = self._DISABLED_TOOLTIP_MIN_WIDTH if self.__isDisabled(index) else (self._STACK_TOOLTIP_MIN_WIDTH if isStack else self._NO_STACK_TOOLTIP_MIN_WIDTH)
        self._setWidth(width)
        if isStack and hasRandomBonusCap:
            self._setMargins(5, 5)
        else:
            self._setMargins(-5, -5)
        if self.__isDisabled(index):
            return self.__getDisabledBlocks()
        items = [formatters.packBuildUpBlockData(blocks=[self.__getTitle(i18n.makeString(equipment.userString)), self.__getSubTitle()] if isStack and hasRandomBonusCap else [self.__getTitle(i18n.makeString(equipment.userString))]), formatters.packBuildUpBlockData(padding=formatters.packPadding(right=20), blocks=[self.__getContent(i18n.makeString(equipment.shortDescription))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE if isStack else BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE)]
        if hasRandomBonusCap:
            items.append(formatters.packBuildUpBlockData(blocks=[self.__getFooter(self.itemCD)]))
        return items

    @staticmethod
    def __getR():
        return R.strings.fl_tooltips.randomReserve

    @staticmethod
    def __getTitle(title):
        return formatters.packTextBlockData(text=text_styles.middleTitle(title), padding=formatters.packPadding(bottom=8))

    def __getSubTitle(self):
        return formatters.packTextBlockData(text=text_styles.standard(backport.text(self.__getR().characteristic.improved())), padding=formatters.packPadding(top=-8))

    @staticmethod
    def __getContent(content):
        return formatters.packTextBlockData(text=text_styles.main(content))

    def __getFooter(self, intCD):
        return formatters.packTextBlockData(text=text_styles.successBright(backport.text(self.__getR().purchased())) if self.__isPurchased(intCD) else text_styles.error(backport.text(self.__getR().notPurchased())), padding=formatters.packPadding(bottom=1, top=6))

    def __getDisabledBlocks(self):
        return [formatters.packBuildUpBlockData(blocks=[self.__getContent(backport.text(self.__getR().disable()))])]

    @staticmethod
    def __getEquipmentByIntCD(intCD):
        equipments = vehicles.g_cache.equipments()
        _, _, equipmentID = vehicles.parseIntCompactDescr(intCD)
        return equipments.get(equipmentID, None)

    @staticmethod
    def __isPurchased(intCD):
        playerDataComponent = BigWorld.player().arena.componentSystem.playerDataComponent
        return playerDataComponent is not None and intCD in playerDataComponent.purchasedAbilities

    def __isDisabled(self, index):
        equipment = self.__sessionProvider.shared.equipments.getEquipmentByIDx(index - self._RESERVES_OFFSET)
        return not equipment.getQuantity()

    def __isUsed(self, item):
        return item == self.USED_SLOT
