# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/bob/__init__.py
import logging
from gui.Scaleform.daapi.view.lobby.bob.bob_prime_time_view import BobServerPresenter
from predefined_hosts import g_preDefinedHosts
from web.web_client_api import w2c, w2capi, W2CSchema, Field
from helpers import dependency
from skeletons.gui.game_control import IBobController
_logger = logging.getLogger(__name__)

class _GetTokenSchema(W2CSchema):
    token = Field(type=basestring)


@w2capi(name='bob', key='action')
class BobWebApi(W2CSchema):
    __bobController = dependency.descriptor(IBobController)

    @w2c(_GetTokenSchema, name='get_single_token')
    def handleClaimReward(self, cmd):
        if hasattr(cmd, 'token') and cmd.token:
            self.__bobController.claimReward(cmd.token.encode('utf8'))
        else:
            _logger.warning('Token is required!')

    @w2c(W2CSchema, name='check_personal_reward')
    def handleCheckPersonalReward(self, _):
        return self.__bobController.checkPersonalReward()

    @w2c(W2CSchema, name='get_prime_times')
    def getPrimeTimesInfo(self, _):
        result = {}
        servers = self.__buildServersList()
        primeTimes = self.__bobController.getPrimeTimes()
        for pID, primeTime in primeTimes.iteritems():
            if pID in servers:
                server = servers[pID]
                periphery = {}
                periphery['short_name'] = server.getShortName()
                periphery['long_name'] = server.getName()
                periphery['days'] = self.__daysFormatter(primeTime.periods)
                result[pID] = periphery

        return result

    def __timeFormatter(self, timePoint):
        return {'hour': timePoint[0],
         'minute': timePoint[1]}

    def __periodFormatter(self, period):
        return {'start': self.__timeFormatter(period[0]),
         'end': self.__timeFormatter(period[1])}

    def __daysFormatter(self, days):
        formattedDays = {}
        for dayId, periods in days.iteritems():
            formattedDays[dayId] = {periodId:self.__periodFormatter(period) for periodId, period in enumerate(periods)}

        return formattedDays

    def __buildServersList(self):
        allServers = {}
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        for idx, serverData in enumerate(hostsList):
            serverPresenter = BobServerPresenter(idx, *serverData)
            allServers[serverPresenter.getPeripheryID()] = serverPresenter

        return allServers
