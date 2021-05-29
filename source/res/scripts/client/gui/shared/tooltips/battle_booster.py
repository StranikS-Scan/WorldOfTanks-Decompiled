# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/battle_booster.py
import logging
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.module import PriceBlockConstructor
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_TOOLTIP_WIDTH = 468
_AUTOCANNON_SHOT_DISTANCE = 400
_MAX_INSTALLED_LIST_LEN = 10
_DEFAULT_PADDING = 20
_logger = logging.getLogger(__name__)

class BattleBoosterTooltipBlockConstructor(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, module, configuration):
        self.module = module
        self.configuration = configuration

    def construct(self):
        return None


class HeaderBlockConstructor(BattleBoosterTooltipBlockConstructor):

    def construct(self):
        module = self.module
        title = module.userName
        desc = R.strings.tooltips.battleBooster.crew() if module.isCrewBooster() else R.strings.tooltips.battleBooster.optionalDevice()
        overlayPadding = formatters.packPadding(top=SLOT_HIGHLIGHT_TYPES.TOOLTIP_BIG_OVERLAY_PADDING_TOP, left=SLOT_HIGHLIGHT_TYPES.TOOLTIP_BIG_OVERLAY_PADDING_LEFT)
        headerText = formatters.packTitleDescBlock(title=text_styles.highTitle(title), desc=text_styles.standard(backport.text(desc)), gap=-3, padding=formatters.packPadding(top=-6))
        headerImage = formatters.packItemTitleDescBlockData(img=backport.image(self._getIcon()), imgPadding=formatters.packPadding(top=7), overlayPath=backport.image(self._getOverlay()), overlayPadding=overlayPadding, padding=formatters.packPadding(left=120))
        return [headerText, headerImage]

    def _getOverlay(self):
        overlayType = self.module.getOverlayType(vehicle=self.configuration.vehicle)
        overlayPath = R.images.gui.maps.shop.artefacts.c_180x135.dyn('{}_overlay'.format(overlayType))()
        return overlayPath

    def _getIcon(self):
        moduleName = self.module.descriptor.iconName
        icon = R.images.gui.maps.shop.artefacts.c_180x135.dyn(moduleName)
        if icon is None:
            _logger.warn('BattleBooster icon missed: R.images.gui.maps.shop.artefacts.c_180x135.%s', moduleName)
            return ''
        else:
            return icon()


class EpicHeaderBlockConstructor(HeaderBlockConstructor):

    def _getOverlay(self):
        if self.module.isCrewBooster():
            overlayPath = R.images.gui.maps.shop.artefacts.c_180x135.battleBoosterReplace_overlay()
        else:
            overlayPath = R.images.gui.maps.shop.artefacts.c_180x135.battleBooster_overlay()
        return overlayPath


class BattleBoosterBlockTooltipData(BlocksTooltipData):
    itemsCache = dependency.descriptor(IItemsCache)
    _headerBlockConstructor = HeaderBlockConstructor

    def __init__(self, context):
        super(BattleBoosterBlockTooltipData, self).__init__(context, TOOLTIP_TYPE.MODULE)
        self.item = None
        self._setContentMargin(top=0, left=0, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_WIDTH)
        return

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        items = super(BattleBoosterBlockTooltipData, self)._packBlocks()
        module = self.item
        statsConfig = self.context.getStatsConfiguration(module)
        statusConfig = self.context.getStatusConfiguration(module)
        leftPadding = 20
        rightPadding = 20
        bottomPadding = -7
        topPadding = -5
        textGap = -2
        priceWidth = 105
        headerBlock = self._headerBlockConstructor(module, statsConfig).construct()
        if headerBlock:
            items.append(formatters.packBuildUpBlockData(headerBlock, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=20, bottom=-83)))
        effectsBlock = EffectsBlockConstructor(module, statusConfig).construct()
        if effectsBlock:
            items.append(formatters.packBuildUpBlockData(effectsBlock, padding=formatters.packPadding(top=topPadding, left=leftPadding, right=rightPadding, bottom=bottomPadding), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        priceBlock = BattleBoosterPriceBlockConstructor(module, statsConfig, priceWidth, leftPadding, rightPadding).construct()
        if priceBlock:
            items.append(formatters.packBuildUpBlockData(priceBlock, padding=formatters.packPadding(left=10, right=rightPadding, top=topPadding, bottom=-10), gap=textGap))
        statusBlock = StatusBlockConstructor(module, statusConfig).construct()
        if statusBlock:
            items.append(formatters.packBuildUpBlockData(statusBlock, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=topPadding, bottom=-15)))
        boosterIsUseless = BoosterHasNoEffectBlockConstructor(module, statusConfig).construct()
        if boosterIsUseless:
            items.append(formatters.packBuildUpBlockData(boosterIsUseless, gap=-4, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=topPadding, bottom=bottomPadding), stretchBg=False))
        return items


class EpicBattleBoosterBlockTooltipData(BattleBoosterBlockTooltipData):
    _headerBlockConstructor = EpicHeaderBlockConstructor


class BattleBoosterPriceBlockConstructor(PriceBlockConstructor):

    def __init__(self, module, configuration, valueWidth, leftPadding, rightPadding):
        super(BattleBoosterPriceBlockConstructor, self).__init__(module, configuration, valueWidth, leftPadding, rightPadding)
        self._inInventoryBlockData['text'] = TOOLTIPS.BATTLEBOOSTER_INVENTORYCOUNT
        self._inventoryPadding = formatters.packPadding(left=90)
        self._priceLeftPadding = 75


class EffectsBlockConstructor(BattleBoosterTooltipBlockConstructor):

    def construct(self):
        block = []
        module = self.module
        vehicle = self.configuration.vehicle
        header = formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.battleBooster.installationEffects())), padding=formatters.packPadding(bottom=5))
        block.append(header)
        if module.isCrewBooster():
            skillLearnt = module.isAffectedSkillLearnt(vehicle)
            skillName = backport.text(R.strings.item_types.tankman.skills.dyn(module.getAffectedSkillName())())
            replaceText = module.getCrewBoosterAction(True)
            boostText = module.getCrewBoosterAction(False)
            skillNotLearntText = text_styles.standard(backport.text(R.strings.tooltips.battleBooster.skill.not_learnt()))
            skillLearntText = text_styles.standard(backport.text(R.strings.tooltips.battleBooster.skill.learnt()))
            applyStyles = vehicle is not None
            replaceText, boostText = self.__getSkillTexts(skillLearnt, replaceText, boostText, applyStyles)
            block.append(formatters.packImageTextBlockData(title=replaceText, img=backport.image(R.images.gui.maps.icons.buttons.checkmark()) if not skillLearnt and applyStyles else None, imgPadding=formatters.packPadding(left=2, top=3), txtOffset=20))
            block.append(formatters.packImageTextBlockData(title=skillNotLearntText % skillName, txtOffset=20))
            block.append(formatters.packImageTextBlockData(title=boostText, img=backport.image(R.images.gui.maps.icons.buttons.checkmark()) if skillLearnt and applyStyles else None, imgPadding=formatters.packPadding(left=2, top=3), txtOffset=20, padding=formatters.packPadding(top=15)))
            block.append(formatters.packImageTextBlockData(title=skillLearntText % skillName, txtOffset=20))
        else:
            block.append(formatters.packTextParameterBlockData(text_styles.main(module.shortDescription.replace('%s ', '', 1)), text_styles.bonusAppliedText(module.getOptDeviceBoosterGainValue(vehicle=vehicle)), valueWidth=110, gap=15))
        return block

    @staticmethod
    def __getSkillTexts(skillLearnt, replaceText, boostText, applyStyles):
        if applyStyles:
            if skillLearnt:
                return (text_styles.main(replaceText), text_styles.bonusAppliedText(boostText))
            return (text_styles.bonusAppliedText(replaceText), text_styles.main(boostText))
        return (text_styles.main(replaceText), text_styles.main(boostText))


class StatusBlockConstructor(BattleBoosterTooltipBlockConstructor):

    def construct(self):
        block = list()
        if self.configuration.isAwardWindow:
            return block
        else:
            module = self.module
            inventoryVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()
            totalInstalledVehicles = [ x.shortUserName for x in module.getInstalledVehicles(inventoryVehicles) ]
            installedVehicles = totalInstalledVehicles[:_MAX_INSTALLED_LIST_LEN]
            canNotBuyBlock = None
            if module.isHidden:
                canNotBuyBlock = [self.__getCannotBuyBlock(module, self.configuration)]
            if canNotBuyBlock is not None:
                block.append(formatters.packBuildUpBlockData(canNotBuyBlock, padding=formatters.packPadding(top=-4, bottom=-5, right=_DEFAULT_PADDING), gap=4))
            if installedVehicles:
                tooltipText = ', '.join(installedVehicles)
                if len(totalInstalledVehicles) > _MAX_INSTALLED_LIST_LEN:
                    hiddenVehicleCount = len(totalInstalledVehicles) - _MAX_INSTALLED_LIST_LEN
                    hiddenTxt = '%s %s' % (backport.text(R.strings.tooltips.suitableVehicle.hiddenVehicleCount()), text_styles.stats(hiddenVehicleCount))
                    tooltipText = '%s %s' % (tooltipText, hiddenTxt)
                block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.deviceFits.already_installed.header())), desc=text_styles.standard(tooltipText)))
            return block

    @staticmethod
    def __getCannotBuyBlock(module, statusConfig):
        statsVehicle = statusConfig.vehicle
        if statsVehicle is None or module in statsVehicle.battleBoosters.installed or module.isInInventory:
            cannotBuyHeaderStyle = text_styles.warning
        else:
            cannotBuyHeaderStyle = text_styles.critical
        return formatters.packItemTitleDescBlockData(title=cannotBuyHeaderStyle(backport.text(R.strings.tooltips.moduleFits.battleBooster.cannotBuy.header())), desc=text_styles.main(backport.text(R.strings.tooltips.moduleFits.battleBooster.cannotBuy.description())))


class BoosterHasNoEffectBlockConstructor(BattleBoosterTooltipBlockConstructor):

    def construct(self):
        block = list()
        module = self.module
        vehicle = self.configuration.vehicle
        if vehicle is not None and not module.isAffectsOnVehicle(vehicle):
            block.append(formatters.packTextBlockData(text_styles.statusAlert(backport.text(R.strings.tooltips.battleBooster.useless.header()))))
            block.append(formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.battleBooster.useless.body())), padding=formatters.packPadding(top=8)))
        return block
