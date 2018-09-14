# Embedded file name: scripts/client/gui/shared/tooltips/potapovquests.py
import BigWorld
from helpers import i18n
from gui import makeHtmlString
from gui.server_events import g_eventsCache
from gui.shared.tooltips import ToolTipDataField, ToolTipData, TOOLTIP_TYPE, ToolTipMethodField
from gui.shared.utils.gui_items import InventoryVehicle

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


class PrivateQuestsTileDescr(ToolTipDataField):

    def _getValue(self):
        icon = makeHtmlString('html_templates:lobby/tooltips', 'private_quests_icon')
        return i18n.makeString('#tooltips:privateQuests/slot/descr', icon=icon)


class PrivateQuestsTileParamsField(ToolTipDataField):

    def _getValue(self):
        tile = self._tooltip.item
        if tile.isUnlocked():
            achievedTokensCount, _ = tile.getTokensCount()
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
            achievedTokensCount = 0
            competedQStr = recruited = '0'
        result = []
        if not tile.isAwardAchieved():
            result.append(('collectedSheets', BigWorld.wg_getIntegralFormat(achievedTokensCount)))
        result.extend([('competedTasks', competedQStr), ('recruitedTankmanFemale', recruited)])
        return result

    @classmethod
    def __formatParam(cls, curVal, allVal):
        _formatInt = BigWorld.wg_getIntegralFormat
        return makeHtmlString('html_templates:lobby/tooltips', 'private_quests_values', {'current': _formatInt(curVal),
         'all': _formatInt(allVal)})


class PrivateQuestsTileStatusField(ToolTipDataField):

    def _getValue(self):
        tile = self._tooltip.item
        level = InventoryVehicle.STATE_LEVEL.WARNING
        if tile.isCompleted():
            status, level = 'completed', InventoryVehicle.STATE_LEVEL.INFO
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
        chainVehType = tile.getChainVehicleClass(chainID)
        if chainVehType is not None:
            vehicleTypeStr = i18n.makeString('#tooltips:privateQuests/progress/type/%s' % chainVehType)
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
        status, level = 'notReceived', InventoryVehicle.STATE_LEVEL.WARNING
        for quest in tile.getQuests().get(chainID, {}).itervalues():
            if quest.isFinal() and quest.isCompleted():
                status, level = 'received', InventoryVehicle.STATE_LEVEL.INFO
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
