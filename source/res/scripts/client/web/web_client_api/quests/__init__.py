# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/quests/__init__.py
from gui.server_events.bonuses import AllOfBoxBonus
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.server_events import IEventsCache
from web.web_client_api import w2c, w2capi, Field, W2CSchema, WebCommandException
_BONUS_SERIALIZERS = {AllOfBoxBonus: lambda b: b.getBonusList()}

class _QuestTypes(CONST_CONTAINER):
    IN_PROGRESS = 'in_progress'
    ACTIVE = 'active'
    HIDDEN = 'hidden'


def _isValidTypesList(types, _):
    for t in types:
        if t not in _QuestTypes.ALL():
            raise WebCommandException('"{}" is unsupported quest type.'.format(t))

    return True


class _TokensSchema(W2CSchema):
    ids = Field(type=list, required=False)


class _QuestsSchema(W2CSchema):
    ids = Field(type=list, required=False)
    types = Field(type=list, required=False, validator=_isValidTypesList)


@w2capi(name='user_data', key='action')
class QuestsWebApi(W2CSchema):
    __eventsCache = dependency.descriptor(IEventsCache)

    @w2c(_QuestsSchema, 'get_tokens')
    def handleGetTokens(self, command):
        tokens = self.__eventsCache.questsProgress.getTokensData()
        return {'token_list': self.__filteredByIDs(tokens, command.ids),
         'action': 'get_tokens'}

    @w2c(_QuestsSchema, 'get_quests')
    def handleGetQuests(self, command):
        types = command.types
        quests = {}
        if not types:
            quests.update(self.__getInProgressQuestData())
        else:
            if _QuestTypes.IN_PROGRESS in types:
                quests.update(self.__getInProgressQuestData())
            if _QuestTypes.HIDDEN in types:
                quests.update(self.__getQuestsData(lambda q: q.isHidden(), getAll=True))
            if _QuestTypes.ACTIVE in types:
                quests.update(self.__getQuestsData())
        return {'quest_list': self.__filteredByIDs(quests, command.ids),
         'action': 'get_quests'}

    def __filteredByIDs(self, data, ids):
        return data if not ids else {k:v for k, v in data.iteritems() if k in ids}

    def __getInProgressQuestData(self):
        quests = self.__eventsCache.questsProgress.getQuestsData()
        quests.update(self.__getQuestsData(lambda q: q.getID() in quests, getAll=True))
        return quests

    def __getQuestsData(self, filterFunc=None, getAll=False):
        return {questID:{'expiryTime': quest.getData().get('progressExpiryTime'),
         'isDaily': quest.getData().get('isDaily', False),
         'progress': quest.getProgressData(),
         'bonuses': self.__formatBonuses(quest)} for questID, quest in self.__eventsCache.getActiveQuests(filterFunc, getAll).iteritems()}

    def __formatBonuses(self, quest):
        return {bonus.getName():_BONUS_SERIALIZERS.get(bonus.__class__, lambda b: {})(bonus) for bonus in quest.getBonuses()}
