# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/rewards/__init__.py
import itertools
from dossiers2.custom.records import DB_ID_TO_RECORD
from gui.shared.gui_items.dossier import getAchievementFactory
from web.web_client_api import W2CSchema, Field, w2capi, w2c
from helpers import i18n, dependency
from skeletons.gui.server_events import IEventsCache

class _RequestMedalsSchema(W2CSchema):
    medal_ids = Field(required=True, type=list, default=[])


class _RequestQuestBonusSchema(W2CSchema):
    token_base = Field(required=True, type=basestring, default='')


@w2capi(name='rewards', key='action')
class RewardsWebApi(W2CSchema):

    @w2c(_RequestMedalsSchema, 'get_medals')
    def requestRewardInfo(self, cmd):
        responseData = []
        for recordId in cmd.medal_ids:
            record = DB_ID_TO_RECORD.get(int(recordId), ('', ''))
            _, rewardId = record
            factory = getAchievementFactory(record).create()
            responseData.append({'medal_id': recordId,
             'image': ''.join(('gui/maps/icons/achievement/', rewardId, '.png')),
             'title': ''.join(('#achievements:', rewardId)),
             'name': factory.getUserName(),
             'description': factory.getUserWebDescription(),
             'condition': factory.getUserCondition()})

        return responseData

    @w2c(_RequestQuestBonusSchema, 'get_quest_bonuses')
    def requestQuestBonusesInfo(self, cmd):
        return getBonusesInfoByQuestsBaseToken(tokenBase=cmd.token_base)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getBonusesInfoByQuestsBaseToken(tokenBase, eventsCache=None):
    awardsData = {}
    allQuests = eventsCache.getAllQuests()
    for questKey, questData in allQuests.iteritems():
        if tokenBase in questKey:
            questBonuses = questData.getBonuses()
            awardsData[questKey] = _packBonuses(bonuses=questBonuses)

    return awardsData


def _packBonuses(bonuses):
    return list(itertools.chain.from_iterable([ bonus.getWrappedEpicBonusList() for bonus in bonuses ]))
