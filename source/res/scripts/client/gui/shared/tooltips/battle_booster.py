# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/battle_booster.py
import logging
import typing
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen_utils import INVALID_RES_ID
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items.perk import PerkGUI
from gui.shared.items_parameters import formatters as param_formatter
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.module import PriceBlockConstructor
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items.components.detachment_constants import NO_DETACHMENT_ID
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.artefacts import BattleBooster
    from gui.shared.gui_items.detachment import Detachment
    from gui.shared.tooltips.contexts import StatusConfiguration
    from gui.shared.gui_items.Vehicle import Vehicle
_TOOLTIP_WIDTH = 468
_AUTOCANNON_SHOT_DISTANCE = 400
_MAX_INSTALLED_LIST_LEN = 10
_DEFAULT_PADDING = 20
_DEFAULT_MAX_PERK_LEVEL = 10
_logger = logging.getLogger(__name__)

class BattleBoosterTooltipBlockConstructor(object):
    itemsCache = dependency.descriptor(IItemsCache)
    detachmentCache = dependency.descriptor(IDetachmentCache)

    def __init__(self, module, configuration):
        self.module = module
        self.configuration = configuration
        self.vehicle = self.itemsCache.items.getVehicleCopy(self.configuration.vehicle)
        capacity = self.vehicle.battleBoosters.layout.getCapacity()
        if capacity > 0:
            self.vehicle.battleBoosters.layout[0] = self.module
            self.vehicle.battleBoosters.setInstalled(*self.vehicle.battleBoosters.layout)

    def construct(self):
        return None

    @property
    def detachment(self):
        detInvID = self.configuration.vehicle.getLinkedDetachmentID()
        return self.detachmentCache.getDetachment(detInvID)

    @property
    def maxPerkLevel(self):
        if not self.detachment:
            return _DEFAULT_MAX_PERK_LEVEL
        perkID, _, _ = self.module.getPerkBonus()
        return self.detachment.perksMatrix.perks.get(perkID).max_points

    @property
    def perkGUI(self):
        perkID, _, _ = self.module.getPerkBonus()
        return PerkGUI(perkID, self.perkLevelWithBooster)

    @property
    def perkLevel(self):
        if not self.detachment:
            return 0
        perkID, _, _ = self.module.getPerkBonus()
        build = self.detachment.build
        return build.get(perkID, 0)

    @property
    def perkLevelWithBooster(self):
        if not self.detachment:
            _, levelIncrease, _ = self.module.getPerkBonus()
            return levelIncrease
        perkID, _, _ = self.module.getPerkBonus()
        finalPerks = self.detachment.getPerks(vehicle=self.vehicle)
        return finalPerks.get(perkID, 0)

    @property
    def boosterInfluence(self):
        if not self.detachment:
            _, levelIncrease, _ = self.module.getPerkBonus()
            return levelIncrease
        boosterInfluence = self.detachment.getPerksBoosterInfluence(vehicle=self.vehicle)
        return sum((points for intCD, _, points, _ in boosterInfluence if intCD == self.module.intCD))


class HeaderBlockConstructor(BattleBoosterTooltipBlockConstructor):

    def construct(self):
        module = self.module
        title = module.userName
        desc = R.strings.tooltips.battleBooster.crew() if module.isCrewBooster() else R.strings.tooltips.battleBooster.optionalDevice()
        overlayPadding = formatters.packPadding(top=SLOT_HIGHLIGHT_TYPES.TOOLTIP_BIG_OVERLAY_PADDING_TOP, left=SLOT_HIGHLIGHT_TYPES.TOOLTIP_BIG_OVERLAY_PADDING_LEFT)
        headerText = formatters.packTitleDescBlock(title=text_styles.highTitle(title), desc=text_styles.standard(backport.text(desc)), gap=-2, padding=formatters.packPadding(top=-8))
        headerImage = formatters.packItemTitleDescBlockData(img=backport.image(self._getIcon()), overlayPath=backport.image(self._getOverlay()), overlayPadding=overlayPadding, padding=formatters.packPadding(left=120, top=-15, bottom=-97))
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

    def __init__(self, context, isShortened=False):
        super(BattleBoosterBlockTooltipData, self).__init__(context, TOOLTIP_TYPE.MODULE)
        self.item = None
        self._setContentMargin(top=0, left=0, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_WIDTH)
        self._isShortened = isShortened
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
        effectsBlock = EffectsBlockConstructor(module, statusConfig, self._isShortened).construct()
        if effectsBlock:
            headerBlock.extend(effectsBlock)
        if headerBlock:
            items.append(formatters.packBuildUpBlockData(headerBlock, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=20, bottom=0)))
        effectsListBlock, hasSituationalBonus = EffectsListBlockConstructor(module, statusConfig).construct()
        if effectsListBlock:
            items.append(formatters.packBuildUpBlockData(effectsListBlock, padding=formatters.packPadding(top=topPadding, left=leftPadding, right=rightPadding, bottom=-11)))
        if hasSituationalBonus:
            situationalInfo = SituationalBlockConstructor(module, statusConfig).construct()
            items.append(formatters.packBuildUpBlockData(situationalInfo, padding=formatters.packPadding(top=topPadding, left=leftPadding, right=rightPadding, bottom=bottomPadding)))
        workingPrinciple = WorkingPrincipleConstructor(module, statusConfig).construct()
        if workingPrinciple:
            items.append(formatters.packBuildUpBlockData(workingPrinciple, padding=formatters.packPadding(top=topPadding, left=leftPadding, right=rightPadding, bottom=bottomPadding), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        if not self._isShortened:
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
    detachmentCache = dependency.descriptor(IDetachmentCache)

    def __init__(self, module, configuration, isShortened):
        super(EffectsBlockConstructor, self).__init__(module, configuration)
        self._isShortened = isShortened

    def construct(self):
        block = []
        module = self.module
        vehicle = self.configuration.vehicle
        header = formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.battleBooster.installationEffects())))
        block.append(header)
        if module.isCrewBooster():
            perkGUI = self.perkGUI
            level = self.perkLevelWithBooster
            levelIncrease = self.boosterInfluence
            isOvercapped = level > self.maxPerkLevel
            crewBooster = R.strings.tooltips.detachment.crewBooster
            perkName = text_styles.stats(backport.text(perkGUI.name))
            currentLevel = text_styles.stats(level)
            desc = text_styles.main(backport.text(crewBooster.perkName(), name=perkName))
            if not self._isShortened:
                desc = '{} {}'.format(desc, text_styles.main(backport.text(crewBooster.perkProgress(), current=currentLevel, max=self.maxPerkLevel)))
            textStyle = text_styles.whiteOrangeTitleBig if isOvercapped else text_styles.blueBoosterTitleBig
            linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_RED_BOOSTER_LINKAGE if isOvercapped else BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_BLUE_BOOSTER_LINKAGE
            block.append(formatters.packImageTextBlockData(linkage=linkage, title=textStyle('+{}'.format(levelIncrease)), desc=desc, img=backport.image(R.images.gui.maps.icons.perks.normal.c_48x48.dyn(perkGUI.icon)()), padding=formatters.packPadding(left=20, bottom=-8), imgPadding=formatters.packPadding(left=-2), txtOffset=58, txtGap=-4))
        else:
            block.append(formatters.packTextParameterBlockData(text_styles.main(module.shortDescription.replace('%s ', '', 1)), text_styles.bonusAppliedText(module.getOptDeviceBoosterGainValue(vehicle=vehicle)), valueWidth=110, gap=15))
        return block


class EffectsListBlockConstructor(BattleBoosterTooltipBlockConstructor):

    def construct(self):
        block = []
        module = self.module
        hasSituationalBonus = False
        if module.isCrewBooster():
            for bName, value, isSituational in self.perkGUI.getBonusFromBoost(self.perkLevel, self.boosterInfluence):
                bDescrResId = R.strings.tank_setup.kpi.bonus.longDescr.dyn(bName)()
                if bDescrResId == INVALID_RES_ID:
                    bDescrResId = R.strings.tank_setup.kpi.bonus.dyn(bName)()
                bName = backport.text(bDescrResId)
                if not bName:
                    continue
                if isSituational:
                    icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_TOOLTIP_ASTERISK_OPTIONAL, 16, 16, -2)
                    bName = param_formatter.packSituationalIcon(bName, icon)
                    hasSituationalBonus = True
                textStyle = text_styles.statusAttention if isSituational else text_styles.bonusAppliedText
                value = '+' + value if value > 0 else value
                block.append(formatters.packTextParameterBlockData(name=bName, value=textStyle(value), valueWidth=64, gap=14, padding=formatters.packPadding(left=-1, bottom=3)))

        return (block, hasSituationalBonus)


class SituationalBlockConstructor(BattleBoosterTooltipBlockConstructor):

    def construct(self):
        block = []
        text = backport.text(R.strings.tooltips.detachment.crewBooster.isSituational())
        block.append(formatters.packImageTextBlockData(title=text_styles.standard(text), img=RES_ICONS.MAPS_ICONS_TOOLTIP_ASTERISK_OPTIONAL, padding=formatters.packPadding(left=18, bottom=-8), imgPadding=formatters.packPadding(top=3)))
        return block


class WorkingPrincipleConstructor(BattleBoosterTooltipBlockConstructor):
    detachmentCache = dependency.descriptor(IDetachmentCache)

    def construct(self):
        block = []
        module = self.module
        if module.isCrewBooster():
            perkID, levelIncrease, levelOvercap = module.getPerkBonus()
            perk = PerkGUI(perkID, levelIncrease)
            perkName = backport.text(perk.name)
            level = self.perkLevelWithBooster
            isOvercapped = level > self.maxPerkLevel
            crewBooster = R.strings.tooltips.detachment.crewBooster
            header = formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(crewBooster.workingPrinciple())), padding=formatters.packPadding(bottom=3, top=-1))
            block.append(header)
            pointRange = backport.text(R.strings.tooltips.range.common(), left=0, right=self.maxPerkLevel - 1)
            textStyle = text_styles.blueBooster if not isOvercapped else text_styles.main
            pointStyle = text_styles.blueBoosterTitle if not isOvercapped else text_styles.mainTitle
            title = textStyle(backport.text(crewBooster.lowLevel(), points=pointStyle(levelIncrease), name=perkName))
            desc = text_styles.standard(backport.text(crewBooster.lowLevelExpl(), range=pointRange))
            img = backport.image(R.images.gui.maps.icons.buttons.checkmark_blue()) if not isOvercapped else None
            block.append(formatters.packImageTextBlockData(title=title, desc=desc, img=img, imgPadding=formatters.packPadding(left=-6, top=-5), txtOffset=18, txtGap=-2))
            block.append(formatters.packSeparatorBlockData(img=RES_ICONS.MAPS_ICONS_COMPONENTS_TOOLTIP_TOOL_TIP_SEPARATOR, paddings=formatters.packPadding(top=4, bottom=9), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
            textStyle = text_styles.whiteOrange if isOvercapped else text_styles.main
            pointStyle = text_styles.whiteOrangeTitle if isOvercapped else text_styles.mainTitle
            linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_RED_BOOSTER_LINKAGE if isOvercapped else BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_BLOCK_LINKAGE
            title = textStyle(backport.text(crewBooster.highLevel(), points=pointStyle(levelOvercap), name=perkName))
            desc = text_styles.standard(backport.text(crewBooster.highLevelExpl()))
            block.append(formatters.packImageTextBlockData(title=title, linkage=linkage, desc=desc, img=backport.image(R.images.gui.maps.icons.buttons.checkmark_red()) if isOvercapped else None, imgPadding=formatters.packPadding(left=-6, top=-5), txtOffset=18, txtGap=-2, padding=formatters.packPadding(bottom=-1)))
        return block


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
            if module.isCrewBooster() and vehicle.getLinkedDetachmentID() == NO_DETACHMENT_ID:
                text = R.strings.tooltips.battleBooster.useless.needRetrain.body()
            else:
                text = R.strings.tooltips.battleBooster.useless.wrongModule.body()
            block.append(formatters.packTextBlockData(text=text_styles.main(backport.text(text)), padding=formatters.packPadding(top=2, bottom=-1)))
        return block
