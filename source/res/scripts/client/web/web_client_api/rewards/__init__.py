# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/rewards/__init__.py
import itertools
from dossiers2.custom.account_layout import ACCOUNT_DOSSIER_BLOCKS
from dossiers2.custom.records import DB_ID_TO_RECORD
from gui.server_events.bonuses import HIDDEN_BONUSES
from gui.shared.gui_items.dossier import getAchievementFactory
from web.web_client_api import W2CSchema, Field, w2capi, w2c, WebCommandException
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache

def _achievementBlockValidator(block, _=None):
    if block not in ACCOUNT_DOSSIER_BLOCKS:
        raise WebCommandException('unsupported achievement block "{}"'.format(block))
    return True


class _RequestMedalsSchema(W2CSchema):
    medal_ids = Field(type=list, default=[])


class _RequestQuestBonusSchema(W2CSchema):
    quest_id_base = Field(type=basestring, default='')


class _RequestAchievementsSchema(W2CSchema):
    medal_ids = Field(type=list, default=[])
    achievement_block = Field(type=basestring, validator=_achievementBlockValidator, default='singleAchievements')


@w2capi(name='rewards', key='action')
class RewardsWebApi(W2CSchema):
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)

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
        return self.__getBonusesInfoByQuestsBaseToken(questIdBase=cmd.quest_id_base)

    @w2c(_RequestAchievementsSchema, 'get_achievements_from_dossier')
    def getAchievements(self, cmd):
        dossier = self.itemsCache.items.getAccountDossier()
        achievements = dossier.getDossierDescr().expand(cmd.achievement_block)
        result = {achievementId:achievements[achievementId] for achievementId in cmd.medal_ids if achievementId in achievements}
        return result

    def __getBonusesInfoByQuestsBaseToken(self, questIdBase):
        awardsData = {}
        allQuests = self.eventsCache.getAllQuests(filterFunc=lambda q: q.getID().startswith(questIdBase))
        for questKey, questData in allQuests.iteritems():
            questBonuses = questData.getBonuses()
            awardsData[questKey] = list(itertools.chain.from_iterable([ bonus.getWrappedEpicBonusList() for bonus in questBonuses if not isinstance(bonus, HIDDEN_BONUSES) ]))

        return awardsData
