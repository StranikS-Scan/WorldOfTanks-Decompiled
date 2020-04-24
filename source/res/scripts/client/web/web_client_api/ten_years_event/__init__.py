# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ten_years_event/__init__.py
from helpers import dependency
from skeletons.gui.game_control import ITenYearsCountdownController
from web.web_client_api import W2CSchema, Field, w2capi, w2c
from ten_year_countdown_config import FIRST_BLOCK_NUMBER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.awards_formatters import AWARDS_SIZES, AWARDS_SIZES_EXT
from dossiers2.custom.records import DB_ID_TO_RECORD
from gui.shared.gui_items.dossier import getAchievementFactory
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.app_loader import IAppLoader
from gui.shared.gui_items.dossier.achievements.abstract.stage import StageAchievement
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as TC
from ten_year_countdown_config import BLOCK_TOKEN_TEMPLATE

class _RequestQuestBonusSchema(W2CSchema):
    quest_id_base = Field(required=True, type=basestring, default='')


class _RequestMedalsSchema(W2CSchema):
    medal_id = Field(required=True, type=int)
    stage = Field(required=False, type=int, default=0)
    current_block = Field(required=False, type=int, default=1)


class _ShowMedalTooltipSchema(W2CSchema):
    medal_id = Field(required=True, type=int)
    stage = Field(required=False, type=int, default=0)
    current_block = Field(required=False, type=int, default=1)


@w2capi(name='ten_years_event', key='action')
class TenYCEventWebApi(W2CSchema):
    __countdownController = dependency.descriptor(ITenYearsCountdownController)
    __eventCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __appLoader = dependency.descriptor(IAppLoader)

    @w2c(W2CSchema, 'blocks')
    def requestBlocksInfo(self, _):
        responseData = {'blocks': [],
         'eventEnd': None}
        for block in range(FIRST_BLOCK_NUMBER, self.__countdownController.getBlocksCount() + 1):
            dates = self.__countdownController.getActivePhaseDates(block)
            responseData['blocks'].append({'start': dates.start,
             'end': dates.finish})

        responseData['eventEnd'] = self.__countdownController.getEventFinish()
        return responseData

    @w2c(_RequestQuestBonusSchema, 'get_quest_descr')
    def requestQuestDescr(self, cmd):
        questInfo = {}
        questIdBase = cmd.quest_id_base
        allQuests = self.__eventCache.getAllQuests(filterFunc=lambda q: q.getID().startswith(questIdBase))
        for _, questData in allQuests.iteritems():
            questInfo['title'] = questData.getUserName()
            questInfo['description'] = questData.getDescription()
            guestId = questData.getID()
            iconKey = guestId[len(questIdBase):].lstrip('_')
            if iconKey:
                iconBig = RES_ICONS.get128ConditionIcon(iconKey)
                iconSmall = RES_ICONS.get90ConditionIcon(iconKey)
                questInfo['icon'] = {AWARDS_SIZES.BIG: iconBig,
                 AWARDS_SIZES.SMALL: iconSmall}
                return questInfo

        return questInfo

    @w2c(_RequestMedalsSchema, 'get_medal_data')
    def requestMedalData(self, cmd):
        record = DB_ID_TO_RECORD.get(int(cmd.medal_id), ('', ''))
        dossier = self.__itemsCache.items.getAccountDossier()
        achievement = getAchievementFactory(record, dossier).create()
        stage = int(cmd.stage)
        if stage != 0 and isinstance(achievement, StageAchievement):
            if stage < 0:
                stage = achievement.getValue()
                if not self.__isBlockBattleQuestDone(cmd.current_block):
                    stage += 1
                    achievement = getAchievementFactory(record).create(stage)
            else:
                achievement = getAchievementFactory(record).create(stage)
        else:
            stage = achievement.getValue()
        icons = {AWARDS_SIZES_EXT.HUGE: achievement.getIcon110x110(),
         AWARDS_SIZES_EXT.BIG: achievement.getIcon80x80(),
         AWARDS_SIZES_EXT.SMALL: achievement.getIcon48x48()}
        responseData = {'medal_id': cmd.medal_id,
         'icon': icons,
         'name': achievement.getUserName(),
         'description': achievement.getUserWebDescription(),
         'condition': achievement.getUserCondition(),
         'stage': stage}
        return responseData

    @w2c(_ShowMedalTooltipSchema, 'show_medal_tooltip')
    def showTooltip(self, cmd):
        record = DB_ID_TO_RECORD.get(int(cmd.medal_id), ('', ''))
        dossier = self.__itemsCache.items.getAccountDossier()
        achievement = getAchievementFactory(record, dossier).create()
        stage = int(cmd.stage)
        if stage != 0 and isinstance(achievement, StageAchievement):
            if stage < 0:
                stage = achievement.getValue()
                if not self.__isBlockBattleQuestDone(cmd.current_block):
                    stage += 1
                    achievement = getAchievementFactory(record).create(stage)
            else:
                achievement = getAchievementFactory(record).create(stage)
        args = [None,
         None,
         None,
         None,
         None]
        self.__appLoader.getApp().getToolTipMgr().createTypedTooltipExt(TC.ACHIEVEMENT, args, 'INFO', achievement)
        return

    @staticmethod
    def __isBlockBattleQuestDone(blockNum):
        blockTokenName = BLOCK_TOKEN_TEMPLATE.format(blockNum)
        tokens = TenYCEventWebApi.__eventCache.questsProgress.getTokenNames()
        return blockTokenName in tokens
