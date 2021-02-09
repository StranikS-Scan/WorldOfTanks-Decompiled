# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/quests/__init__.py
import itertools
import sys
import typing
from gui.server_events.bonuses import HIDDEN_BONUSES
from gui.Scaleform.daapi.view.lobby.missions.cards_formatters import CardBattleConditionsFormatters
from gui.server_events.cond_formatters import CONDITION_SIZE
from helpers import dependency, i18n
from skeletons.gui.game_control import IMarathonEventsController
from skeletons.gui.server_events import IEventsCache
from web.web_client_api import w2c, w2capi, Field, W2CSchema
from gui.server_events.event_items import Quest
from web.web_client_api.common import sanitizeResPath

class _QuestsSchema(W2CSchema):
    ids = Field(type=list)


class _RawQuestConditionsFormatters(CardBattleConditionsFormatters):
    MAX_CONDITIONS_IN_CARD = sys.maxint
    ICON_SIZE = CONDITION_SIZE.NORMAL

    def _getFormattedField(self, field):
        return i18n.makeString(*field.args)


def _formatQuestConditions(quest):
    formatter = _RawQuestConditionsFormatters()
    conditions = formatter.format(quest)
    return [ {'description': cond['description'],
     'title': cond['title'],
     'type': cond['state'],
     'icon': sanitizeResPath(cond['icon']),
     'progress': cond['progress']} for cond in itertools.chain.from_iterable((component['data'] for component in conditions)) ]


def _formatQuestBonuses(quest):
    entries = []
    for bonus in quest.getBonuses():
        if any((isinstance(bonus, hb) for hb in HIDDEN_BONUSES)):
            continue
        for item in bonus.getWrappedEpicBonusList():
            icon = {size:sanitizeResPath(path) for size, path in item.get('icon').iteritems()}
            entries.append({'id': item.get('id', 0),
             'type': item['type'],
             'icon': icon,
             'value': item.get('value', 0)})

    return entries


def _questAsDict(quest):
    return {'id': quest.getID(),
     'description': quest.getDescription(),
     'name': quest.getUserName(),
     'conditions': _formatQuestConditions(quest),
     'bonuses': _formatQuestBonuses(quest),
     'is_completed': quest.isCompleted(),
     'priority': quest.getPriority()}


@w2capi(name='user_data', key='action')
class QuestsWebApi(W2CSchema):
    _eventsCache = dependency.descriptor(IEventsCache)
    _marathonsCtrl = dependency.descriptor(IMarathonEventsController)

    @w2c(_QuestsSchema, 'get_tokens')
    def handleGetTokens(self, command):
        tokens = self._eventsCache.questsProgress.getTokensData()
        if hasattr(command, 'ids') and command.ids:
            tokens = {k:v for k, v in tokens.iteritems() if k in command.ids}
        return {'token_list': tokens,
         'action': 'get_tokens'}

    @w2c(_QuestsSchema, 'get_quests')
    def handleGetQuests(self, command):
        if command.ids is not None:

            def filterFunc(quest):
                return quest.getID() in command.ids

        else:
            filterFunc = None
        data = {qID:_questAsDict(quest) for qID, quest in self._eventsCache.getActiveQuests(filterFunc=filterFunc).iteritems()}
        return data

    @w2c(_QuestsSchema, 'get_quests_old')
    def handleGetQuestsOld(self, command):

        def _processQuest(progressData, questData):
            data = {}
            if questData is not None:
                data.update({'startTime': questData.getStartTime(),
                 'startTimeLeft': questData.getStartTimeLeft(),
                 'finishTime': questData.getFinishTime(),
                 'finishTimeLeft': questData.getFinishTimeLeft()})
            data.update(progressData)
            return data

        quests = self._eventsCache.questsProgress.getQuestsData()
        if hasattr(command, 'ids') and command.ids:
            quests = {k:v for k, v in quests.iteritems() if k in command.ids}
        quests = {k:_processQuest(v, self._eventsCache.getHiddenQuests().get(k)) for k, v in quests.items()}
        return {'quest_list': quests,
         'action': 'get_quests'}

    @w2c(_QuestsSchema, 'get_step')
    def handleGetStep(self, command):
        if hasattr(command, 'custom_parameters') and 'prefix' in command.custom_parameters:
            marathon = self._marathonsCtrl.getMarathon(command.custom_parameters['prefix'])
            if marathon is not None:
                currentStep, allSteps = marathon.getMarathonProgress()
                return {'current_step': currentStep,
                 'all_steps': allSteps}
        return
