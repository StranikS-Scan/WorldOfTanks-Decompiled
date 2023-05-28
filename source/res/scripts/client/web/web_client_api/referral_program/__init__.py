# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/referral_program/__init__.py
from constants import RP_PGB_POINT, RP_POINT
from gui.shared.gui_items.processors.referral_program import CollectRPPgbPointsProcessor
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IReferralProgramController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from web.web_client_api import w2c, w2capi, W2CSchema, Field

class _CloseReferralProgramViewSchema(W2CSchema):
    pass


class _OpenContentPage(W2CSchema):
    url = Field(required=True, type=basestring)


@w2capi(name='referral_program', key='action')
class ReferralProgramWebApi(W2CSchema):
    __referralCtrl = dependency.descriptor(IReferralProgramController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @w2c(_CloseReferralProgramViewSchema, 'close_referral_program_view')
    def closeReferralProgramView(self, cmd):
        if self.__referralCtrl:
            self.__referralCtrl.hideWindow()

    @w2c(W2CSchema, name='get_rp_pgb_info')
    def getRPPgbInfo(self, _):
        rpPgbPoints = self.__itemsCache.items.stats.entitlements.get(RP_PGB_POINT, 0)
        rpPoints = self.__itemsCache.items.stats.entitlements.get(RP_POINT, 0)
        pgbLimitPoints = self.__itemsCache.items.refProgram.getRPPgbPoints()
        timeLeft = max(self.__itemsCache.items.refProgram.getRPExpirationTime() - int(getServerUTCTime()), 0)
        configLimits = self.__lobbyContext.getServerSettings().getRPConfig().asDict()
        passiveIncome = self.__itemsCache.items.refProgram.getRPPassiveIncome()
        return {'rp_pgb_points': rpPgbPoints,
         'rp_points': rpPoints,
         'rp_pgb_limit_points': pgbLimitPoints,
         'rp_time_left': timeLeft,
         'rp_config_limits': configLimits,
         'rp_passive_income': passiveIncome}

    @w2c(W2CSchema, name='collect_rp_pgb_points')
    def collectRPPgbPoints(self, _):
        success, error = False, ''
        processor = CollectRPPgbPointsProcessor()
        response = yield processor.request()
        if response:
            success, error = response.success, response.userMsg
        else:
            error = 'Undefined server error'
        yield {'success': success,
         'error': error}
