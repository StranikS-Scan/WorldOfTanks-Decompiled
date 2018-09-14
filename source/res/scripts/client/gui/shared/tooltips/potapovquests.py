# Embedded file name: scripts/client/gui/shared/tooltips/potapovquests.py
import BigWorld
from helpers import i18n
from gui import makeHtmlString
from gui.server_events import g_eventsCache
from gui.shared.tooltips import ToolTipDataField, ToolTipData, TOOLTIP_TYPE, ToolTipMethodField, formatters
from gui.shared.gui_items.Vehicle import Vehicle
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.formatters import icons
from gui.shared.tooltips import contexts

class PrivateQuestsTileMethodField(ToolTipMethodField):

    def buildData(self):
        tName = self._getValue()
        return (self._name, i18n.makeString('#tooltips:privateQuests/slot/header', name=tName))


class PrivateQuestsTileConditions(ToolTipDataField):

    def _getValue(self):
        tile = self._tooltip.item
        if tile is not None:
            _, awardTokensCount = tile.getTokensCount()
            totalTokensCount = tile.getTotalTokensCount()
            icon = makeHtmlString('html_templates:lobby/tooltips', 'private_quests_icon')
            return makeHtmlString('html_templates:lobby/tooltips', 'private_quests_conditions', {'condition1': self.__formatCondition('vehicle', awardTokensCount, icon),
             'condition2': self.__formatCondition('anim', totalTokensCount, icon)})
        else:
            return ''

    @classmethod
    def __formatCondition(cls, condition, tokensCount, icon):
        valIcon = makeHtmlString('html_templates:lobby/tooltips', 'private_quests_val_icon', {'count': tokensCount,
         'icon': icon})
        return i18n.makeString('#tooltips:privateQuests/slot/condition/%s' % condition, icon=valIcon)


class PrivateQuestsFalloutTileConditions(ToolTipDataField):

    def _getValue(self):
        return makeHtmlString('html_templates:lobby/tooltips', 'private_quests_conditions', {'condition1': i18n.makeString(TOOLTIPS.PRIVATEQUESTSFALLOUT_SLOT_CONDITION_VEHICLE),
         'condition2': i18n.makeString(TOOLTIPS.PRIVATEQUESTS_SLOT_CONDITION_ANIM)})


class PrivateQuestsTileDescr(ToolTipDataField):

    def _getValue(self):
        icon = makeHtmlString('html_templates:lobby/tooltips', 'private_quests_icon')
        return i18n.makeString('#tooltips:privateQuests/slot/descr', icon=icon)


class BasePrivateQuestsTileParamsField(ToolTipDataField):

    def _getValue(self):
        tile = self._tooltip.item
        if tile.isUnlocked():
            completedQuestsCount = len(tile.getCompletedQuests())
            totalFinalQuestsCount = len(tile.getFinalQuests())
            if tile.isCompleted():
                competedQStr = BigWorld.wg_getIntegralFormat(completedQuestsCount)
                recruited = BigWorld.wg_getIntegralFormat(totalFinalQuestsCount)
            else:
                allQuestsCount = tile.getQuestsCount()
                completedFinalQuestsCount = len(tile.getCompletedFinalQuests(isRewardReceived=True))
                competedQStr = self.__formatParam(completedQuestsCount, allQuestsCount)
                recruited = self.__formatParam(completedFinalQuestsCount, totalFinalQuestsCount)
        else:
            competedQStr = recruited = '0'
        return [('competedTasks', competedQStr), ('recruitedTankmanFemale', recruited)]

    @classmethod
    def __formatParam(cls, curVal, allVal):
        _formatInt = BigWorld.wg_getIntegralFormat
        return makeHtmlString('html_templates:lobby/tooltips', 'private_quests_values', {'current': _formatInt(curVal),
         'all': _formatInt(allVal)})


class PrivateQuestsTileParamsField(BasePrivateQuestsTileParamsField):

    def _getValue(self):
        result = super(PrivateQuestsTileParamsField, self)._getValue()
        tile = self._tooltip.item
        if tile.isUnlocked():
            achievedTokensCount, _ = tile.getTokensCount()
        else:
            achievedTokensCount = 0
        if not tile.isAwardAchieved():
            result.insert(0, ('collectedSheets', BigWorld.wg_getIntegralFormat(achievedTokensCount)))
        return result


class PrivateQuestsTileStatusField(ToolTipDataField):

    def _getValue(self):
        tile = self._tooltip.item
        level = Vehicle.VEHICLE_STATE_LEVEL.WARNING
        if tile.isCompleted():
            status, level = 'completed', Vehicle.VEHICLE_STATE_LEVEL.INFO
        elif tile.isInProgress():
            status = 'inProgress'
        elif tile.isUnlocked():
            status = 'available'
        else:
            status = 'lock'
        textKey = '#tooltips:privateQuests/status/{0}/{1}'.format(status, 'descr')
        return {'header': i18n.makeString('#tooltips:privateQuests/status/{0}/{1}'.format(status, 'header')),
         'text': i18n.makeString(textKey) if i18n.doesTextExist(textKey) else None,
         'level': level}


class PrivateQuestsChainNameField(ToolTipDataField):

    def _getValue(self):
        tileID, chainID = self._tooltip.item
        tile = g_eventsCache.potapov.getTiles()[tileID]
        chainMajorTag = tile.getChainMajorTag(chainID)
        if chainMajorTag is not None:
            vehicleTypeStr = i18n.makeString('#tooltips:privateQuests/progress/type/%s' % chainMajorTag)
            return i18n.makeString('#tooltips:privateQuests/progress/header', type=vehicleTypeStr)
        else:
            return ''


class PrivateQuestsChainConditionsField(ToolTipDataField):

    def _getValue(self):
        return i18n.makeString('#tooltips:privateQuests/progress/condition')


class PrivateQuestsChainParamsField(ToolTipDataField):

    def _getValue(self):
        tileID, chainID = self._tooltip.item
        tile = g_eventsCache.potapov.getTiles()[tileID]
        tokensCount = tile.getChainTotalTokensCount(chainID, isMainBonuses=True)
        return (('sheets', tokensCount), ('recruitTankmanFemale', ''))


class PrivateQuestsChainStatusField(ToolTipDataField):

    def _getValue(self):
        tileID, chainID = self._tooltip.item
        tile = g_eventsCache.potapov.getTiles()[tileID]
        status, level = 'notReceived', Vehicle.VEHICLE_STATE_LEVEL.WARNING
        for quest in tile.getQuests().get(chainID, {}).itervalues():
            if quest.isFinal() and quest.isCompleted():
                status, level = 'received', Vehicle.VEHICLE_STATE_LEVEL.INFO
                break

        return {'header': i18n.makeString('#tooltips:privateQuests/status/%s/header' % status),
         'text': None,
         'level': level}


class PrivateQuestsChainTooltipData(ToolTipData):

    def __init__(self, context):
        super(PrivateQuestsChainTooltipData, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self.fields = (PrivateQuestsChainNameField(self, 'name'),
         PrivateQuestsChainConditionsField(self, 'conditions'),
         PrivateQuestsChainParamsField(self, 'params'),
         PrivateQuestsChainStatusField(self, 'status'))


class PrivateQuestsTileTooltipData(ToolTipData):

    def __init__(self, context):
        super(PrivateQuestsTileTooltipData, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self.fields = (PrivateQuestsTileMethodField(self, 'name', 'getUserName'),
         PrivateQuestsTileConditions(self, 'conditions'),
         PrivateQuestsTileDescr(self, 'descr'),
         PrivateQuestsTileParamsField(self, 'params'),
         PrivateQuestsTileStatusField(self, 'status'))


class PrivateQuestsFalloutTileTooltipData(ToolTipData):

    def __init__(self, context):
        super(PrivateQuestsFalloutTileTooltipData, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self.fields = (PrivateQuestsTileMethodField(self, 'name', 'getUserName'),
         PrivateQuestsFalloutTileConditions(self, 'conditions'),
         BasePrivateQuestsTileParamsField(self, 'params'),
         PrivateQuestsTileStatusField(self, 'status'))


class SeasonAwardTooltipData(BlocksTooltipData):

    def __init__(self, context, title, image, imgPadding = None):
        super(SeasonAwardTooltipData, self).__init__(context, TOOLTIP_TYPE.PRIVATE_QUESTS)
        self._setContentMargin(top=16, bottom=23)
        self._setWidth(340)
        self.__title = title
        self.__image = image
        self.__imgPadding = imgPadding

    def _packBlocks(self, *args, **kwargs):
        blocks = super(SeasonAwardTooltipData, self)._packBlocks(*args, **kwargs)
        blocks.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(self.__title), formatters.packImageBlockData(self.__image, BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=self.__imgPadding)]))
        return blocks


class FemaleTankmanAwardTooltipData(SeasonAwardTooltipData):

    def __init__(self):
        _ms = i18n.makeString
        super(FemaleTankmanAwardTooltipData, self).__init__(contexts.PotapovQuestsTileContext(), text_styles.highTitle(_ms(TOOLTIPS.QUESTS_SEASONAWARD_TITLE, name=_ms(QUESTS.SEASONAWARDSWINDOW_FEMALETANKMANAWARD_TITLE))), RES_ICONS.MAPS_ICONS_QUESTS_TANKMANFEMALEGRAY, formatters.packPadding(top=22, bottom=13))

    def _packBlocks(self, *args, **kwargs):
        blocks = super(FemaleTankmanAwardTooltipData, self)._packBlocks(*args, **kwargs)
        _ms = i18n.makeString
        blocks.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.main(_ms(TOOLTIPS.QUESTS_SEASONAWARD_FEMALETANKMAN_DESCRIPTION_PART1))), formatters.packTextBlockData(text_styles.standard(_ms(TOOLTIPS.QUESTS_SEASONAWARD_FEMALETANKMAN_DESCRIPTION_PART2)))], gap=11))
        return blocks


class TokensAwardTooltipData(SeasonAwardTooltipData):

    def __init__(self):
        _ms = i18n.makeString
        super(TokensAwardTooltipData, self).__init__(contexts.PotapovQuestsTileContext(), text_styles.highTitle(_ms(TOOLTIPS.QUESTS_SEASONAWARD_TITLE, name=_ms(QUESTS.SEASONAWARDSWINDOW_COMMENDATIONLISTSAWARD_TITLE))), RES_ICONS.MAPS_ICONS_QUESTS_TOKEN256TOOLTIP, formatters.packPadding(top=-46, bottom=7))

    def _packBlocks(self, *args, **kwargs):
        blocks = super(TokensAwardTooltipData, self)._packBlocks(*args, **kwargs)
        blocks.append(formatters.packTextBlockData(text_styles.main(i18n.makeString(TOOLTIPS.QUESTS_SEASONAWARD_TOKENS_DESCRIPTION, icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_QUESTS_TOKEN16, 16, 16, -3, 0)))))
        return blocks
