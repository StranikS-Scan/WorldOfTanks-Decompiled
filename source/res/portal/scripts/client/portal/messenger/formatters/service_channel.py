# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/messenger/formatters/service_channel.py
from gui.impl import backport
from gui.impl.gen import R
from messenger import g_settings
from messenger.formatters.service_channel import BattleResultsFormatter, ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData

class ExtendedBattleResultsFormatter(BattleResultsFormatter):
    _battleResultKeys = {-1: 'portalBattleDefeatResult',
     0: 'portalBattleDrawGameResult',
     1: 'portalBattleVictoryResult'}

    def _prepareFormatData(self, message):
        templateName, ctx = super(ExtendedBattleResultsFormatter, self)._prepareFormatData(message)
        ctx['progressionTokens'] = self.__formatProgressionPoints(message)
        ctx['vehicleUpgradePoints'] = self.__formatVehicleUpgradePoints(message)
        ctx['difficulty'] = self.__getDifficultyDescr(message)
        return (templateName, ctx)

    @staticmethod
    def __formatProgressionPoints(message):
        progressionTokens = message.data.get('progressionTokens', 0)
        return g_settings.htmlTemplates.format('portalBattleResultProgressionPoints', ctx={'progressionTokens': progressionTokens})

    @staticmethod
    def __formatVehicleUpgradePoints(message):
        vehicleUpgradePoints = message.data.get('vehicleUpgradePoints', 0)
        return g_settings.htmlTemplates.format('portalBattleResultVehicleUpgradePoints', ctx={'vehicleUpgradePoints': vehicleUpgradePoints})

    def __getDifficultyDescr(self, message):
        level = message.data.get('portalBattleLevel', 1)
        return backport.text(R.strings.portal_lobby.complexity.level.dyn('c_{}'.format(level))())


class PortalSystemMessageFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'PortalSystemMessage'

    def format(self, message, *args):
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE)
        return [MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE))]
