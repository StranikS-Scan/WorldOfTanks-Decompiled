# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/event.py
import BigWorld
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui import makeHtmlString
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.EVENT import EVENT
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.module import ModuleBlockTooltipData
from helpers import dependency, time_utils, int2roman
from helpers.i18n import makeString as _ms
from gui.prb_control.entities.listener import IGlobalListener
from helpers.statistics import HARDWARE_SCORE_PARAMS
from items import vehicles
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.locale.MENU import MENU

def _timeStringGenerator(key, **kwargs):
    timeStr = _ms('{}/{}'.format(MENU.TIME_TIMEVALUE, key), **kwargs)
    return timeStr.replace(' ', '&nbsp;')


class EventFractionInfoTooltipData(BlocksTooltipData, IGlobalListener):
    _gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(EventFractionInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)

    def _packBlocks(self, generalId, isWrongFront, **kwargs):
        items = super(EventFractionInfoTooltipData, self)._packBlocks()
        general = self._gameEventController.getGeneral(generalId)
        generalLevel = general.getCurrentProgressLevel()
        items.append(self._getHeader(generalId, generalLevel))
        items.append(self._getDescriptionBlock(generalId))
        items.append(self._getVehiclesBlock(generalId, generalLevel))
        items.append(self._getAbilitiesBlock(generalId, generalLevel))
        items.append(self._getLevelsBlock(general))
        if isWrongFront:
            items.append(self._getLockText())
        return items

    def _getHeader(self, generalId, generalLevel):
        return formatters.packTextBlockData(text=text_styles.concatStylesToMultiLine(text_styles.highTitle(_ms(EVENT.getGeneralTooltipHeader(generalId))), text_styles.mainBig(_ms(EVENT.HANGAR_TOOLTIP_GENERAL_GENERALLEVEL, level=int2roman(generalLevel + 1)))))

    def _getDescriptionBlock(self, generalId):
        return formatters.packTextBlockData(text=text_styles.standard(_ms(EVENT.getResultScrGeneralDescription(generalId))))

    def _getVehiclesBlock(self, generalId, generalLevel):
        general = self._gameEventController.getGeneral(generalId)
        vehiclesCDs = general.getVehiclesByLevel(generalLevel)
        vehiclesNames = [ self._itemsCache.items.getItemByCD(vCD).userName for vCD in vehiclesCDs ]
        return self._formatNames(EVENT.HANGAR_TOOLTIP_GENERAL_VEHICLESLIST, vehiclesNames)

    def _getAbilitiesBlock(self, generalId, generalLevel):
        general = self._gameEventController.getGeneral(generalId)
        abilitiesIDs = general.getAbilitiesByLevel(generalLevel)
        abilitiesNames = [ vehicles.g_cache.equipments()[abilityID].userString for abilityID in abilitiesIDs ]
        return self._formatNames(EVENT.HANGAR_TOOLTIP_GENERAL_ABILITYLIST, abilitiesNames)

    def _formatNames(self, mainText, names):
        return formatters.packTextBlockData(text=text_styles.concatStylesToMultiLine(text_styles.main(_ms(mainText)), *[ text_styles.stats(name) for name in names ]))

    def _getLevelsBlock(self, general):
        currentPoints = general.getCurrentProgress()
        body = [text_styles.concatStylesWithSpace(text_styles.main(_ms(EVENT.HANGAR_TOOLTIP_GENERAL_SCORE)), text_styles.stats(currentPoints))]
        generalLevel = general.getCurrentProgressLevel()
        if generalLevel == general.getMaxLevel():
            body.append(text_styles.success(EVENT.HANGAR_MAX_LEVEL))
        else:
            body.extend((self._getPointsLeftFormatted(level, general.getTotalProgressForLevel(level) - currentPoints) for level in xrange(generalLevel + 1, general.getMaxLevel() + 1)))
        return formatters.packTextBlockData(text=text_styles.concatStylesToMultiLine(*body))

    def _getPointsLeftFormatted(self, level, pointsLeft):
        return text_styles.concatStylesWithSpace(text_styles.main(_ms(EVENT.HANGAR_TOOLTIP_GENERAL_NEXTLEVELSCORE, level=int2roman(level + 1))), text_styles.stats(pointsLeft))

    def _getLockText(self):
        return formatters.packAlignedTextBlockData(text_styles.critical(_ms(EVENT.SQUAD_GENERAL_NOT_VALID)), BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)


class EventFractionInfoWinScreenTooltipData(BlocksTooltipData, IGlobalListener):
    _gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(EventFractionInfoWinScreenTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)

    def _packBlocks(self, generalId, earnedPoints, damageDealt, isWin, place, **kwargs):
        items = super(EventFractionInfoWinScreenTooltipData, self)._packBlocks()
        items.append(self._getHeader(generalId, earnedPoints, isWin, place))
        items.append(self._getDescription())
        items.append(self._getScore(damageDealt))
        return items

    def _getHeader(self, generalId, earnedPoints, isWin, place):
        shortDescrKey = EVENT.RESULTSCREEN_TOOLTIP_REWARD_SHORTDESCRLOSE
        if isWin:
            shortDescrKey = EVENT.RESULTSCREEN_TOOLTIP_REWARD_SHORTDESCRWIN
        return formatters.packTextBlockData(text=text_styles.concatStylesToMultiLine(text_styles.highTitle(makeHtmlString('html_templates:lobby/battle_results/', 'tooltip_general_reward', {'text': _ms(EVENT.RESULTSCREEN_TOOLTIP_REWARD_HEADERGENERALWITHPOINTS, name=_ms(EVENT.getGeneralTooltipHeader(generalId)), points=earnedPoints)})), text_styles.mainBig(_ms(shortDescrKey, place=place))))

    def _getDescription(self):
        return formatters.packTextBlockData(text=text_styles.concatStylesToMultiLine(text_styles.standard(_ms(EVENT.RESULTSCREEN_TOOLTIP_REWARD_DESCRIPTION))))

    def _getScore(self, damageDealt):
        return formatters.packTextBlockData(text=text_styles.concatStylesWithSpace(text_styles.main(_ms(EVENT.RESULTSCREEN_TOOLTIP_REWARD_SCORETEXT)), text_styles.stats(str(damageDealt))))


class EventFrontInfoTooltipData(BlocksTooltipData, IGlobalListener):

    def __init__(self, context):
        super(EventFrontInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)

    def _packBlocks(self, frontId, receivedPoints, **kwargs):
        items = super(EventFrontInfoTooltipData, self)._packBlocks()
        items.append(self._getFrontTitle(frontId, receivedPoints))
        items.append(self._getFrontDescription(frontId))
        return items

    def _getFrontTitle(self, frontId, receivedPoints):
        return formatters.packTextBlockData(text_styles.highTitle(makeHtmlString('html_templates:lobby/battle_results/', 'tooltip_front_reward', {'text': _ms(EVENT.RESULTSCREEN_TOOLTIP_REWARD_HEADERGENERALWITHPOINTS, name=_ms(EVENT.getResultScrFrontTitle(frontId)), points=receivedPoints)})))

    def _getFrontDescription(self, frontId):
        return formatters.packTextBlockData(text_styles.main(_ms(EVENT.getResultScrFrontDescription(frontId))))


class EventEnergyInfoTooltipData(BlocksTooltipData, IGlobalListener):
    gameEventController = dependency.descriptor(IGameEventController)
    _BLOCK_GAP = 10

    def __init__(self, context):
        super(EventEnergyInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)

    def _packBlocks(self, *args, **kwargs):
        items = super(EventEnergyInfoTooltipData, self)._packBlocks()
        energy = self.gameEventController.getEnergy()
        energyCount = energy.getCurrentCount()
        body = [formatters.packTitleDescBlockSmallTitle(text_styles.middleTitle(EVENT.HANGAR_TOOLTIP_ENERGY_TITLE), text_styles.main(EVENT.HANGAR_TOOLTIP_ENERGY_DESC)), formatters.packTextBlockData(text_styles.main(_ms(EVENT.HANGAR_TOOLTIP_ENERGY_AVAILABLE_NOW, value=text_styles.hightlight(str(energyCount)))))]
        expectedEnergyOnNextDay = energy.getExpectedEnergyOnNextDay()
        if expectedEnergyOnNextDay > 0:
            timeLeft = energy.getTimeLeftToRecharge()
            if timeLeft is not None:
                timeLeftStr = text_styles.middleTitle(time_utils.getTillTimeString(timeLeft, MENU.TIME_TIMEVALUE, sourceStrGenerator=_timeStringGenerator))
                body.append(formatters.packTextBlockData(text_styles.main(_ms(EVENT.HANGAR_TOOLTIP_ENERGY_AVAILABLE_IN_FUTURE, value=text_styles.middleTitle(str(expectedEnergyOnNextDay)), time=timeLeftStr))))
        items.append(formatters.packBuildUpBlockData(body, self._BLOCK_GAP))
        return items


class EventBannerInfoTooltipData(BlocksTooltipData, IGlobalListener):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, context):
        super(EventBannerInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)

    def _packBlocks(self, *args, **kwargs):
        items = super(EventBannerInfoTooltipData, self)._packBlocks()
        energy = self.gameEventController.getEnergy()
        energyCount = energy.getCurrentCount()
        body = [formatters.packTitleDescBlockSmallTitle(text_styles.highTitle(EVENT.HANGARBANNER_TOOLTIP_HEADER), text_styles.standard(EVENT.HANGARBANNER_TOOLTIP_DESCRIPTION)), formatters.packTextBlockData(text_styles.main(_ms(EVENT.HANGAR_TOOLTIP_ENERGY_AVAILABLE_NOW, value=text_styles.middleTitle(str(energyCount)))))]
        expectedEnergyOnNextDay = energy.getExpectedEnergyOnNextDay()
        if expectedEnergyOnNextDay > 0:
            timeLeft = energy.getTimeLeftToRecharge()
            if timeLeft is not None:
                timeLeftStr = text_styles.middleTitle(time_utils.getTillTimeString(timeLeft, MENU.TIME_TIMEVALUE, sourceStrGenerator=_timeStringGenerator))
                valueStr = text_styles.middleTitle(str(expectedEnergyOnNextDay))
                body.append(formatters.packTextBlockData(text_styles.main(_ms(EVENT.HANGAR_TOOLTIP_ENERGY_AVAILABLE_IN_FUTURE, value=valueStr, time=timeLeftStr))))
        fronts = self.gameEventController.getFronts()
        maxRewards = len(fronts)
        unlockedRewards = sum((1 for front in fronts.itervalues() if front.isCompleted()))
        valueStr = text_styles.middleTitle(_ms(EVENT.HANGARBANNER_TOOLTIP_REWARDSVALUE, value=str(unlockedRewards), maxValue=str(maxRewards)))
        body.append(formatters.packTextBlockData(text_styles.main(_ms(EVENT.HANGARBANNER_TOOLTIP_REWARDS, value=valueStr))))
        items.append(formatters.packBuildUpBlockData(body))
        return items


class EventModuleBlockTooltipData(ModuleBlockTooltipData):
    gameEventController = dependency.descriptor(IGameEventController)

    def _packBlocks(self, *args, **kwargs):
        moduleArgs = args[:-1]
        frontID = args[-1]
        front = self.gameEventController.getFront(frontID)
        isCompleted = front.items and front.items[-1].isCompleted()
        body = [formatters.packTitleDescBlockSmallTitle(text_styles.highTitle(EVENT.getRewardTooltipHeader(frontID)), text_styles.standard(EVENT.getRewardTooltipDescription(frontID)))]
        if not isCompleted:
            progressMaxValue = front.getTotalProgress()
            progressValue = min(front.getCurrentProgress(), progressMaxValue)
            marksMaxValue = front.getFrontMarksTotalCount()
            marksValue = front.getFrontMarksCount()
            body.append(formatters.packTextBlockData(text_styles.main(_ms(EVENT.REWARDMODULE_TOOLTIP_PROGRESS, value=text_styles.middleTitle(_ms(EVENT.HANGARBANNER_TOOLTIP_PROGRESSVALUE, value=progressValue, maxValue=progressMaxValue))))))
            body.append(formatters.packTextBlockData(text_styles.main(_ms(EVENT.REWARDMODULE_TOOLTIP_PROGRESSMARKS, value=text_styles.middleTitle(_ms(EVENT.HANGARBANNER_TOOLTIP_PROGRESSVALUE, value=marksValue, maxValue=marksMaxValue))))))
        else:
            body.append(formatters.packTextBlockData(text_styles.middleBonusTitle(EVENT.REWARDMODULE_TOOLTIP_ACHIEVED)))
        items = [formatters.packBuildUpBlockData(body, padding=formatters.packPadding(left=20, right=20, top=20))]
        items.extend(super(EventModuleBlockTooltipData, self)._packBlocks(*moduleArgs, **kwargs))
        return items


class _PerformanceGroup(object):
    HIGH_RISK = 1
    MEDIUM_RISK = 2
    LOW_RISK = 3


class _LimitType(object):
    SYSTEM_DATA = 0
    HARDWARE_PARAMS = 1


_PERFORMANCE_GROUP_LIMITS = {_PerformanceGroup.HIGH_RISK: [{_LimitType.SYSTEM_DATA: {'osBit': 1,
                                                         'graphicsEngine': 0}}, {_LimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_MEMORY: 490}}, {_LimitType.SYSTEM_DATA: {'graphicsEngine': 0},
                                _LimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_RAM: 2900}}],
 _PerformanceGroup.MEDIUM_RISK: [{_LimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_SCORE: 150}}, {_LimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_CPU_SCORE: 50000}}]}

class EventSelectorWarningTooltip(BlocksTooltipData):
    settingsCore = dependency.descriptor(ISettingsCore)
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, context):
        super(EventSelectorWarningTooltip, self).__init__(context, None)
        self._setContentMargin(top=17, left=18, bottom=20, right=20)
        self._setMargins(afterBlock=0)
        self._setWidth(width=367)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(EventSelectorWarningTooltip, self)._packBlocks(*args, **kwargs)
        items.append(self.__packDescriptionBlock())
        items.append(self.__packEnergyInfoBlock())
        items.append(self.__getPerformanceWarningText())
        return items

    def __packDescriptionBlock(self):
        return formatters.packTitleDescBlock(title=text_styles.highTitle(EVENT.SELECTORTOOLTIP_HEADER), desc=text_styles.main(EVENT.SELECTORTOOLTIP_DESCRIPTION))

    def __packEnergyInfoBlock(self):
        energy = self.gameEventController.getEnergy()
        energyCount = energy.getCurrentCount()
        body = [formatters.packTextBlockData(text_styles.main(_ms(EVENT.HANGAR_TOOLTIP_ENERGY_AVAILABLE_NOW, value=text_styles.middleTitle(str(energyCount)))))]
        expectedEnergyOnNextDay = energy.getExpectedEnergyOnNextDay()
        if expectedEnergyOnNextDay > 0:
            timeLeft = energy.getTimeLeftToRecharge()
            if timeLeft is not None:
                timeLeftStr = text_styles.middleTitle(time_utils.getTillTimeString(timeLeft, MENU.TIME_TIMEVALUE, sourceStrGenerator=_timeStringGenerator))
                valueStr = text_styles.middleTitle(str(expectedEnergyOnNextDay))
                body.append(formatters.packTextBlockData(text_styles.main(_ms(EVENT.HANGAR_TOOLTIP_ENERGY_AVAILABLE_IN_FUTURE, value=valueStr, time=timeLeftStr))))
        return formatters.packBuildUpBlockData(body)

    def __getPerformanceWarningText(self):
        performanceGroup = self.__analyzeClientSystem()
        if performanceGroup == _PerformanceGroup.HIGH_RISK:
            block = formatters.packTitleDescBlock(title=text_styles.concatStylesWithSpace(icons.markerBlocked(), text_styles.error(EVENT.SELECTORTOOLTIP_ASSUREDLOWPERFORMANCE_TITLE)), desc=text_styles.main(EVENT.SELECTORTOOLTIP_ASSUREDLOWPERFORMANCE_DESCRIPTION))
        elif performanceGroup == _PerformanceGroup.MEDIUM_RISK:
            block = formatters.packTitleDescBlock(title=text_styles.concatStylesWithSpace(icons.alert(), text_styles.alert(EVENT.SELECTORTOOLTIP_POSSIBLELOWPERFORMANCE_TITLE)), desc=text_styles.main(EVENT.SELECTORTOOLTIP_POSSIBLELOWPERFORMANCE_DESCRIPTION))
        else:
            block = formatters.packTextBlockData(text=text_styles.concatStylesWithSpace(icons.info(), text_styles.main(EVENT.SELECTORTOOLTIP_INFORMATIVELOWPERFORMANCE_DESCRIPTION)))
        return block

    def __analyzeClientSystem(self):
        stats = BigWorld.wg_getClientStatistics()
        stats['graphicsEngine'] = self.settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE)
        performanceGroup = _PerformanceGroup.LOW_RISK
        for groupName, conditions in _PERFORMANCE_GROUP_LIMITS.iteritems():
            for currentLimit in conditions:
                condValid = True
                systemStats = currentLimit.get(_LimitType.SYSTEM_DATA, {})
                for key, limit in systemStats.iteritems():
                    currValue = stats.get(key, None)
                    if currValue is None or currValue != limit:
                        condValid = False

                hardwareParams = currentLimit.get(_LimitType.HARDWARE_PARAMS, {})
                for key, limit in hardwareParams.iteritems():
                    currValue = BigWorld.getAutoDetectGraphicsSettingsScore(key)
                    if currValue >= limit:
                        condValid = False

                if condValid:
                    performanceGroup = groupName
                    break

        return performanceGroup


class EventGeneralProgressionInfoTooltipData(BlocksTooltipData, IGlobalListener):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, context):
        super(EventGeneralProgressionInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)

    def _packBlocks(self, generalId, **kwargs):
        items = super(EventGeneralProgressionInfoTooltipData, self)._packBlocks()
        general = self._gameEventController.getGeneral(generalId)
        items.append(self._getHeader(generalId))
        items.append(self._getDescriptionBlock())
        items.append(self._getLevelsBlock(general))
        return items

    def _getHeader(self, generalId):
        return formatters.packTextBlockData(text=text_styles.concatStylesToMultiLine(text_styles.highTitle(_ms(EVENT.GENERALS_PROGRESSION_HEADER, name=_ms(EVENT.getGeneralTooltipHeader(generalId))))))

    def _getDescriptionBlock(self):
        return formatters.packTextBlockData(text=text_styles.standard(_ms(EVENT.GENERALS_PROGRESSION_DESCRIPTION)))

    def _formatNames(self, mainText, names):
        return formatters.packTextBlockData(text=text_styles.concatStylesToMultiLine(text_styles.main(_ms(mainText)), *[ text_styles.stats(name) for name in names ]))

    def _getLevelsBlock(self, general):
        currentPoints = general.getCurrentProgress()
        body = [text_styles.concatStylesWithSpace(text_styles.main(_ms(EVENT.HANGAR_TOOLTIP_GENERAL_SCORE)), text_styles.stats(currentPoints))]
        generalLevel = general.getCurrentProgressLevel()
        if generalLevel == general.getMaxLevel():
            body.append(text_styles.success(EVENT.HANGAR_MAX_LEVEL))
        else:
            body.extend((self._getPointsLeftFormatted(level, general.getTotalProgressForLevel(level) - currentPoints) for level in xrange(generalLevel + 1, general.getMaxLevel() + 1)))
        return formatters.packTextBlockData(text=text_styles.concatStylesToMultiLine(*body))

    def _getPointsLeftFormatted(self, level, pointsLeft):
        return text_styles.concatStylesWithSpace(text_styles.main(_ms(EVENT.HANGAR_TOOLTIP_GENERAL_NEXTLEVELSCORE, level=int2roman(level + 1))), text_styles.stats(pointsLeft))
