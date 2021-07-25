# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/detachment.py
from itertools import izip
from CurrentVehicle import g_currentVehicle
from crew2 import settings_globals
from goodies.goodie_constants import RECERTIFICATION_FORM_ID
from gui import makeHtmlString
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from gui.impl import backport
from gui.impl.auxiliary.detachmnet_convert_helper import getDetachmentFromVehicle
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_tooltip_model import PerkTooltipModel
from gui.impl.lobby.detachment.tooltips.commander_perk_tooltip import CommanderPerkTooltip
from gui.impl.lobby.detachment.tooltips.crew_retrain_penalty_tooltip import CrewRetrainPenaltyTooltip
from gui.impl.lobby.detachment.tooltips.detachment_preview_tooltip import DetachmentPreviewTooltip
from gui.impl.lobby.detachment.tooltips.perk_tooltip import PerkTooltip
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters, ToolTipBaseData
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class DetachmentSellLimitTooltipData(BlocksTooltipData):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _DEFAULT_PROGRESSION_LAYOUT_ID = 1

    def __init__(self, context):
        super(DetachmentSellLimitTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setContentMargin(bottom=8)
        self._setWidth(width=315)

    def _packBlocks(self, progressionLayoutID=None, **kwargs):
        items = super(DetachmentSellLimitTooltipData, self)._packBlocks()
        sellLimit = self.lobbyContext.getServerSettings().getDetachmentSellsDailyLimit()
        curSellCount = max(sellLimit - self.itemsCache.items.stats.detachmentSellsLeft, 0)
        detLevel = self._getTrashLevel(progressionLayoutID)
        items.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.detachment.dismiss.disable.header())), desc=text_styles.main(makeHtmlString('html_templates:lobby/detachment', 'sellLimit', ctx={'sellLimit': sellLimit,
         'curSellCount': curSellCount,
         'detLevel': detLevel}))))
        return items

    def _getTrashLevel(self, progressionLayoutID=None):
        if progressionLayoutID is None:
            progressionLayoutID = self._DEFAULT_PROGRESSION_LAYOUT_ID
        progressionSettings = settings_globals.g_detachmentSettings.progression
        progression = progressionSettings.getProgressionByID(progressionLayoutID)
        return progression.getRawLevelByXP(settings_globals.g_detachmentSettings.garbageThreshold)


class DetachmentRecycleBinFullData(BlocksTooltipData):
    detachmentCache = dependency.descriptor(IDetachmentCache)

    def __init__(self, context):
        super(DetachmentRecycleBinFullData, self).__init__(context, TOOLTIP_TYPE.QUESTS)

    def _packBlocks(self, *args, **kwargs):
        items = super(DetachmentRecycleBinFullData, self)._packBlocks()
        maxCount = text_styles.stats(settings_globals.g_detachmentSettings.recycleBinMaxSize)
        demobilizedDetachments = self.detachmentCache.getDetachments(REQ_CRITERIA.DETACHMENT.DEMOBILIZE)
        currCount = text_styles.stats(len(demobilizedDetachments))
        items.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.dismissDetachment.bufferIsFull.header())), desc=text_styles.main(backport.text(R.strings.tooltips.dismissDetachment.bufferIsFull.body(), maxCount=maxCount, currCount=currCount))))
        return items


class DetachmentPreviewTooltipContentWindowData(ToolTipBaseData):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(DetachmentPreviewTooltipContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.DETACHMENT_PREVIEW)

    def getDisplayableData(self, *args, **kwargs):
        vehicle = g_currentVehicle.item
        recruits = [ (self.itemsCache.items.getTankman(recruit.invID) if recruit else None) for _, recruit in vehicle.crew ]
        recruitsWithSlots = list(enumerate(recruits))
        detDescr, instDescrs, _, skinID = getDetachmentFromVehicle(vehicle, recruitsWithSlots)
        return DecoratedTooltipWindow(DetachmentPreviewTooltip(vehicle, detDescr, instDescrs, skinID), useDecorator=False)


class DetachmentPerkTooltipContentWindowData(ToolTipBaseData):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(DetachmentPerkTooltipContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.GF_DETACHMENT_PERK)

    def getDisplayableData(self, perkID, *args, **kwargs):
        return DecoratedTooltipWindow(PerkTooltip(perkID, detachmentInvID=g_detachmentTankSetupVehicle.currentDetachmentID, tooltipType=PerkTooltipModel.TTC_PERK_TOOLTIP, tempPoints=g_detachmentTankSetupVehicle.getPerkPointsWithExtraBonus(int(perkID))), useDecorator=False)


class CrewRetrainPenaltyTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(CrewRetrainPenaltyTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.CREW_RETRAIN_PENALTY)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(CrewRetrainPenaltyTooltip(*args, **kwargs), useDecorator=False)


class RecertificationFormToolTipData(BlocksTooltipData):
    _WIDTH = 365
    __goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, context):
        super(RecertificationFormToolTipData, self).__init__(context, TOOLTIP_TYPE.RECERTIFICATION_FORM)
        self._setContentMargin(top=15, left=19, bottom=16, right=13)
        self._setWidth(self._WIDTH)

    def _packBlocks(self, *args, **kwargs):
        activeGoodies = self.__goodiesCache.getRecertificationForms(REQ_CRITERIA.DEMOUNT_KIT.IN_ACCOUNT | REQ_CRITERIA.DEMOUNT_KIT.IS_ENABLED)
        recertificationForms = activeGoodies.get(RECERTIFICATION_FORM_ID, None)
        count = recertificationForms.count if recertificationForms else 0
        valueFormatter = text_styles.critical if count == 0 else text_styles.stats
        return [formatters.packTitleDescAsComplexBlock(backport.text(R.strings.tooltips.detachment.recertification.header()), backport.text(R.strings.tooltips.detachment.recertification.description()), headerStyle=text_styles.middleTitle), formatters.packBuildUpBlockData([formatters.packTitleDescParameterWithIconBlockData(title=text_styles.main(backport.text(R.strings.tooltips.vehicle.inventoryCount())), value=valueFormatter(count), icon=backport.image(R.images.gui.maps.icons.library.storage_icon()), padding=formatters.packPadding(left=105, bottom=-10), titlePadding=formatters.packPadding(left=-2), iconPadding=formatters.packPadding(top=-2, left=-2))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE), formatters.packTextParameterBlockData(name='', value='', padding=formatters.packPadding(bottom=-16))]


class DormitoryInfoToolTipData(BlocksTooltipData):
    _WIDTH = 320

    def __init__(self, context):
        super(DormitoryInfoToolTipData, self).__init__(context, None)
        self._setContentMargin(top=15, left=19, bottom=18, right=13)
        self._setMargins(afterBlock=7)
        self._setWidth(self._WIDTH)
        return

    def _packBlocks(self, *args, **kwargs):
        return [formatters.packTitleDescAsComplexBlock(backport.text(R.strings.tooltips.detachment.dormitory.header()), backport.text(R.strings.tooltips.detachment.dormitory.body()), headerStyle=text_styles.middleTitle)]


class InstructorBonusesToolTipData(BlocksTooltipData):
    detachmentCache = dependency.descriptor(IDetachmentCache)
    _WIDTH = 354
    LOCALIZATION_KEYS_BY_CLASS_ID = [{'common': backport.text(R.strings.tooltips.detachment.instructorBonuses.commonBonusWithValue()),
      'extra': backport.text(R.strings.tooltips.detachment.instructorBonuses.extraBonusWithValue())}, {'common': backport.text(R.strings.tooltips.detachment.instructorBonuses.commonBonus()),
      'extra': backport.text(R.strings.tooltips.detachment.instructorBonuses.extraBonus())}, {'common': backport.text(R.strings.tooltips.detachment.instructorBonuses.commonBonus())}]

    class BonusHolder(object):

        def get(self, active):
            pass

        def isInRange(self, perkLevel):
            return False

        @property
        def isOvercap(self):
            return False

        def _formatBonus(self, msg, active):
            return makeHtmlString('html_templates:lobby/detachment/InstructorBonuses/BonusPoints', ('Overcap' if self.isOvercap else 'Active') if active else 'Common', {'msg': msg})

        def _getValueText(self, value, active):
            instructorBonusesPoints = R.strings.tooltips.detachment.instructorBonuses.points
            pointsDescr = instructorBonusesPoints.overcap.num(value) if self.isOvercap else instructorBonusesPoints.withoutOvercap.num(value)
            value = backport.text(R.strings.tooltips.detachment.instructorBonuses.points.value(), value=value)
            formattedValue = makeHtmlString('html_templates:lobby/detachment/InstructorBonuses', 'WordSelection', {'msg': value}) if not active else value
            formattedValue = makeHtmlString('html_templates:lobby/detachment/InstructorBonuses', 'Bold', {'msg': formattedValue})
            return backport.text(pointsDescr(), formattedPoints=formattedValue)

    class GiveIfInRange(BonusHolder):

        def __init__(self, value, rangeStart, rangeEnd):
            super(InstructorBonusesToolTipData.GiveIfInRange, self).__init__()
            self._value = value
            self._rangeStart = rangeStart
            self._rangeEnd = rangeEnd

        def get(self, active, mult=False):
            key_ = 'giveIfInRangeMult' if mult else 'giveIfInRange'
            return self._formatBonus(backport.text(R.strings.tooltips.detachment.instructorBonuses.bonusesBlock.common.dyn(key_)(), value=self._getValueText(self._value, active), rangeStart=self._rangeStart, rangeEnd=self._rangeEnd), active)

        def isInRange(self, perkLevel):
            return self._rangeStart < perkLevel and perkLevel <= self._rangeEnd

    class GiveIfMore(BonusHolder):

        def __init__(self, value1, value2):
            super(InstructorBonusesToolTipData.GiveIfMore, self).__init__()
            self._value1 = value1
            self._value2 = value2

        def get(self, active, mult=False):
            key = 'giveIfMoreMult' if mult else 'giveIfMore'
            return self._formatBonus(backport.text(R.strings.tooltips.detachment.instructorBonuses.bonusesBlock.common.dyn(key)(), points=self._getValueText(self._value1, active), levelForOverride=self._value2), active)

        def isInRange(self, perkLevel):
            return perkLevel >= self._value2

        @property
        def isOvercap(self):
            return True

    def __init__(self, context):
        super(InstructorBonusesToolTipData, self).__init__(context, None)
        self._setWidth(self._WIDTH)
        self._setMargins(afterBlock=7)
        self._setContentMargin(top=12, left=19, bottom=-6)
        return

    def _packBlocks(self, instructor, *args, **kwargs):
        return [self._makeTooltipDescriptionBlock(instructor), self._makeBonusesBlock(instructor), self._makeBonusPointsDescriptionBlock()]

    def _formatSelected(self, msg):
        return makeHtmlString('html_templates:lobby/detachment/InstructorBonuses', 'WordSelection', {'msg': msg})

    def _makeTooltipDescriptionBlock(self, instructor):
        classID = instructor.classID
        bonusClass = instructor.bonusClass
        perksCount = len(bonusClass.perkPoints)
        info = {'bonusesCount': perksCount}
        info.update(self.LOCALIZATION_KEYS_BY_CLASS_ID[classID - 1])
        selectedValues = {key:self._formatSelected(value) for key, value in info.iteritems()}
        instBonuses = R.strings.tooltips.detachment.instructorBonuses
        message = backport.text(instBonuses.descriptionBlock.num(classID)(), **selectedValues)
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.highTitle(backport.text(instBonuses.header())), padding=formatters.packPadding(bottom=2)), formatters.packImageTextBlockData(desc=text_styles.main(message), descLeading=-2)])

    def _makeBonusesBlock(self, instructor):
        bonusClass = instructor.bonusClass
        perksCount = len(bonusClass.perkPoints)
        level = bonusClass.levelRules[0]
        commonBonuses = [self.GiveIfInRange(bonusClass.perkPoints[0], 0, level), self.GiveIfMore(bonusClass.overcapPoints[0], level + 1)]
        commonPerksCount = max(perksCount - 1, 1)
        commonPerksIDs = [ k for k, _, _ in instructor.bonusPerksList[0:commonPerksCount] ]
        det = self.detachmentCache.getDetachment(instructor.detInvID)
        instBonusesBlock = R.strings.tooltips.detachment.instructorBonuses.bonusesBlock
        instInvID = instructor.invID
        perksInRange = self.__getPerksInRange(det, instInvID, commonBonuses, commonPerksIDs)
        handlers = commonBonuses
        blocksList = []
        if perksInRange and len(perksInRange[0]) > 1:
            blocksList.append(self._makeBonusBlock(handlers, instBonusesBlock.common.header.first(), perksInRange, 0))
            blocksList.append(self._makeBonusBlock(handlers, instBonusesBlock.common.header.second(), perksInRange, 1))
        elif commonPerksCount == 1:
            blocksList.append(self._makeBonusBlock(handlers, instBonusesBlock.common.header.single(), perksInRange, 0))
        else:
            blocksList.append(self._makeBonusBlock(handlers, instBonusesBlock.common.header.double(), perksInRange, 0, True))
        if perksCount > 1:
            overcapPoints = bonusClass.overcapPoints[perksCount - 1]
            extraBonuses = [self.GiveIfInRange(overcapPoints, 0, level), self.GiveIfMore(overcapPoints, level + 1)]
            extraPerksIDs = [instructor.bonusPerksList[perksCount - 1][0]] if instructor.bonusPerksList else []
            isPerksInRange = self.__getPerksInRange(det, instInvID, extraBonuses, extraPerksIDs)
            blocksList.append(self._makeBonusBlock(extraBonuses, instBonusesBlock.extra.header(), isPerksInRange, 0))
        return formatters.packBuildUpBlockData(blocks=blocksList, padding=formatters.packPadding(top=-3, bottom=-7), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _makeBonusBlock(self, handlers, headerDyn, isPerksInRange, index, mult=False):
        blocksLocal = []
        for active, handler in izip((l[index] for l in isPerksInRange), handlers):
            desc = handler.get(active, mult)
            blocksLocal.append(self._getActiveBonusBlock(desc, handler.isOvercap) if active else self._getCommonBonusBlock(desc))

        return formatters.packBuildUpBlockData(blocks=[formatters.packTextBlockData(text_styles.middleTitle(backport.text(headerDyn)), padding=formatters.packPadding(bottom=7)), formatters.packBuildUpBlockData(blocks=blocksLocal, gap=-7)], gap=-7, padding=formatters.packPadding(bottom=-14))

    def _getActiveBonusBlock(self, desc, overcap):
        buttons = R.images.gui.maps.icons.buttons
        linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_RED_BOOSTER_LINKAGE if overcap else BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_BLUE_BOOSTER_LINKAGE
        return formatters.packBuildUpBlockData([formatters.packImageTextBlockData(linkage=linkage, img=backport.image(buttons.checkmark_red() if overcap else buttons.checkmark_blue()), ignoreImageSize=True, padding=formatters.packPadding(top=-2, left=-10), blockWidth=16), formatters.packImageTextBlockData(title=desc, padding=formatters.packPadding(top=3, left=-5), blockWidth=298, descLeading=-2, linkage=linkage)], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL)

    def _getCommonBonusBlock(self, desc, offset=0):
        return formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.detachment.icons.bullet()), imgPadding=formatters.packPadding(top=8, left=2 + offset), desc=desc, padding=formatters.packPadding(top=3, bottom=7), descLeading=-2, blockWidth=314)

    def _getBonusPointDescriptionsIter(self):
        index = 0
        while True:
            bonusPointDescr = R.strings.tooltips.detachment.instructorBonuses.bonusPointsDescription.num(index)
            if bonusPointDescr:
                yield backport.text(bonusPointDescr())
                index += 1
            break

    def _makeBonusPointsDescriptionBlock(self):
        blocksLocal = []
        for bonusPointDescription in self._getBonusPointDescriptionsIter():
            blocksLocal.append(self._getCommonBonusBlock(makeHtmlString('html_templates:lobby/detachment/InstructorBonuses', 'BonusPointsDescription', {'msg': bonusPointDescription}), 21))

        return formatters.packBuildUpBlockData(blocks=[formatters.packTextBlockData(makeHtmlString('html_templates:lobby/detachment/InstructorBonuses', 'BonusPointsDescriptionHeader'), padding=formatters.packPadding(top=-7, left=-1, bottom=-5)), formatters.packBuildUpBlockData(blocks=blocksLocal, gap=-12)])

    def __getPerksInRange(self, det, instInvID, perksHandlers, perksIDs):
        perksInOvercap = {perkID:overcapPoints > 0 for instInvID_, perkID, perkPoints, overcapPoints in det.getPerksInstructorInfluence() if instInvID_ == instInvID} if det is not None else {}
        perksIDs = perksIDs if perksIDs else [0]
        return [ [ handler.isOvercap == perksInOvercap.get(perkID) for perkID in perksIDs ] for handler in perksHandlers ]


class CommanderPerkTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(CommanderPerkTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.COMMANDER_PERK_GF)

    def getDisplayableData(self, perkID, *args, **kwargs):
        return DecoratedTooltipWindow(CommanderPerkTooltip(perkType=perkID), useDecorator=False)
