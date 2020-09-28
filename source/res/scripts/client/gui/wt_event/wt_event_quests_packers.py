# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_quests_packers.py
import logging
import typing
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.events.wt_event_quest_model import WtEventQuestModel
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getDetailedMissionData
from gui.server_events.formatters import DECORATION_SIZES
from gui.shared.missions.packers.events import DailyQuestUIDataPacker, findFirstConditionModel
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPacker, packWtQuestBonusModelAndTooltipData
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.common.missions.conditions.preformatted_condition_model import PreformattedConditionModel
_logger = logging.getLogger(__name__)

class WtEventQuestUIDataPacker(DailyQuestUIDataPacker):

    def __init__(self, event):
        super(WtEventQuestUIDataPacker, self).__init__(event)
        self.__isComplete = False

    def pack(self, model=None, tooltipData=None, isComplete=False):
        if model is not None and not isinstance(model, WtEventQuestModel):
            _logger.error('Provided model type is not matching quest type. Expected WtEventQuestModel')
            return
        else:
            model = model if model is not None else WtEventQuestModel()
            self.__tooltipData = tooltipData
            self.__isComplete = isComplete
            self._packModel(model)
            self.__resolveSingleQuestIcon(model)
            return model

    def _packModel(self, model):
        super(WtEventQuestUIDataPacker, self)._packModel(model)
        self._packQuestLimits(model)

    def _packBonuses(self, model):
        packer = getWtEventBonusPacker()
        packWtQuestBonusModelAndTooltipData(self._event, packer, model.getBonuses(), tooltipData=self.__tooltipData)

    def _packPostBattleConds(self, model):
        super(WtEventQuestUIDataPacker, self)._packPostBattleConds(model)
        winIndex = -1
        winCondition = None
        topCondition = None
        conditions = model.postBattleCondition.getItems()
        for index, condition in enumerate(conditions):
            if not condition.getDescrData():
                condition.setDescrData(condition.getTitleData())
            conditionType = condition.getConditionType()
            if conditionType == 'win':
                winIndex = index
                winCondition = condition
            if conditionType == 'results':
                topCondition = condition

        if winCondition is not None and topCondition is not None:
            description = backport.text(R.strings.wt_event.condition.c_and(), winCondition=winCondition.getDescrData(), topCondition=topCondition.getDescrData())
            topCondition.setDescrData(description)
            conditions.remove(winIndex)
        return

    def _getStatus(self):
        return MISSIONS_STATES.COMPLETED if self.__isComplete else super(WtEventQuestUIDataPacker, self)._getStatus()

    def _packQuestLimits(self, model):
        detailedInfo = getDetailedMissionData(self._event)
        info = detailedInfo.getInfo()
        model.setStatusLabel(info.get('statusLabel', ''))

    def __resolveSingleQuestIcon(self, model):
        iconId = self._event.getIconID()
        if iconId is not None and iconId > 0:
            prefetcher = self.eventsCache.prefetcher
            questIcon = prefetcher.getMissionDecoration(iconId, DECORATION_SIZES.DAILY)
            if not questIcon:
                _logger.error('Failed to prefetch quest icon from uiDecorator %s', str(iconId))
        else:
            conditionModel = findFirstConditionModel(model.bonusCondition)
            if conditionModel is None:
                conditionModel = findFirstConditionModel(model.postBattleCondition)
                if conditionModel is None:
                    _logger.warning('No condition found. Unable to define quest icon.')
                    return
            questIcon = conditionModel.getIconKey()
        model.setIcon(questIcon)
        return
