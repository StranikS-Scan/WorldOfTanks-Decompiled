# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/strongholds/__init__.py
import itertools
import logging
from functools import partial
from adisp import adisp_process
from constants import JOIN_FAILURE, PREBATTLE_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.server_events.bonuses import BattleTokensBonus
from helpers import dependency
from gui import DialogsInterface
from gui.impl.lobby.stronghold.stronghold_helpers import getClanSeasonProgressLevel, CLAN_SEASON_PROGRESS_PREFIX, CLAN_SEASON_QUEST_PREFIX, STYLE_PROGRESS_PREFIX
from gui.SystemMessages import pushMessage, SM_TYPE
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction, LeavePrbAction
from gui.prb_control.entities.base.external_battle_unit.base_external_battle_ctx import CreateBaseExternalUnitCtx, JoinBaseExternalUnitCtx
from gui.prb_control.formatters import messages
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import actions
from gui.shared.items_parameters import params_helper, formatters
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IReloginController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from web.web_client_api import w2capi, w2c, W2CSchema, Field
_logger = logging.getLogger(__name__)

class _StrongholdsJoinBattleSchema(W2CSchema):
    unit_id = Field(required=True, type=(int, long))
    periphery_id = Field(required=True, type=(int, long))


class _StrongholdsOpenListSchema(W2CSchema):
    extra_params_url = Field(required=False, type=basestring, default='')


class _GetReserveParamsSchema(W2CSchema):
    reserve_intCDs = Field(required=True, type=list)


@w2capi(name='strongholds_battle', key='action')
class StrongholdsWebApi(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __eventsCache = dependency.descriptor(IEventsCache)

    @w2c(_StrongholdsOpenListSchema, 'open_list')
    @adisp_process
    def handleOpenList(self, cmd):
        dispatcher = g_prbLoader.getDispatcher()
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST, extData={'openListExtra': cmd.extra_params_url}))

    @w2c(W2CSchema, 'leave_mode')
    @adisp_process
    def handleLeaveMode(self, cmd):
        dispatcher = g_prbLoader.getDispatcher()
        yield dispatcher.doLeaveAction(LeavePrbAction(isExit=True))

    @w2c(W2CSchema, 'battle_chosen')
    @adisp_process
    def handleBattleChosen(self, cmd):
        dispatcher = g_prbLoader.getDispatcher()

        def onTimeout():
            pushMessage(messages.getJoinFailureMessage(JOIN_FAILURE.TIME_OUT), type=SM_TYPE.Error)
            dispatcher.restorePrevious()

        yield dispatcher.create(CreateBaseExternalUnitCtx(PREBATTLE_TYPE.STRONGHOLD, waitingID='prebattle/create', onTimeoutCallback=onTimeout))

    @w2c(_StrongholdsJoinBattleSchema, 'join_battle')
    @adisp_process
    def handleJoinBattle(self, cmd):

        @adisp_process
        def joinBattle(dispatcher, unitMgrId, onErrorCallback):
            yield dispatcher.join(JoinBaseExternalUnitCtx(unitMgrId, PREBATTLE_TYPE.STRONGHOLD, onErrorCallback=onErrorCallback, waitingID='prebattle/join'))

        def doJoin(restoreOnError):
            dispatcher = g_prbLoader.getDispatcher()

            @adisp_process
            def onError(errorData):
                if restoreOnError:
                    dispatcher.restorePrevious()
                else:
                    yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST))
                try:
                    message = errorData['extra_data']['title']
                    pushMessage(message, type=SM_TYPE.Error)
                except (KeyError, TypeError):
                    LOG_CURRENT_EXCEPTION()

            joinBattle(dispatcher, cmd.unit_id, onError)

        connectionMgr = dependency.instance(IConnectionManager)
        if connectionMgr.peripheryID != cmd.periphery_id:
            success = yield DialogsInterface.showI18nConfirmDialog('changePeriphery')
            if success:
                reloginCtrl = dependency.instance(IReloginController)
                reloginCtrl.doRelogin(cmd.periphery_id, extraChainSteps=(actions.OnLobbyInitedAction(onInited=partial(doJoin, False)),))
        else:
            doJoin(True)

    @w2c(_GetReserveParamsSchema, 'get_reserve_params')
    def getReserveParams(self, cmd):
        result = {}
        for intCD in cmd.reserve_intCDs:
            item = self.__itemsCache.items.getItemByCD(int(intCD))
            if item is None:
                _logger.warning('There is no reserve with intCD=(%s)', intCD)
                continue
            rawParams = params_helper.getParameters(item)
            result[intCD] = {pName:pValue for pName, pValue in formatters.getFormattedParamsList(item.descriptor, rawParams)}

        return result

    @w2c(W2CSchema, 'get_available_peripheries')
    def getAvailablePeripheries(self, _):
        return [ p.peripheryID for p in self.__connectionMgr.availableHosts ]

    @w2c(W2CSchema, 'get_progression_level')
    def getSeasonProgressLevel(self, _):
        return getClanSeasonProgressLevel()

    @w2c(W2CSchema, 'get_quest_bonuses')
    def requestStrongholdQuestBonusesInfo(self, _):
        return self.__getBonusesInfoByQuestsBaseToken(CLAN_SEASON_QUEST_PREFIX)

    @w2c(W2CSchema, 'get_progress_bonuses')
    def requestStrongholdProgressBonusesInfo(self, _):
        return self.__getBonusesInfoByQuestsBaseToken(CLAN_SEASON_PROGRESS_PREFIX)

    def __getBonusesInfoByQuestsBaseToken(self, questIdBase):
        awardsData = {}
        allQuests = self.__eventsCache.getAllQuests(filterFunc=lambda q: q.getID().startswith(questIdBase))
        for questKey, questData in allQuests.iteritems():
            questBonuses = questData.getBonuses()
            rewards = []
            for bonus in questBonuses:
                if isinstance(bonus, BattleTokensBonus):
                    for tokenName in bonus.getTokens().keys():
                        if tokenName == CLAN_SEASON_PROGRESS_PREFIX:
                            rewards.append([{'type': 'token',
                              'value': bonus.getCount(),
                              'name': CLAN_SEASON_PROGRESS_PREFIX}])
                        if tokenName.startswith(STYLE_PROGRESS_PREFIX):
                            rewards.append([{'type': 'token',
                              'name': tokenName}])

                    continue
                rewards.extend([bonus.getWrappedEpicBonusList()])

            awardsData[questKey] = list(itertools.chain.from_iterable(rewards))

        return awardsData
