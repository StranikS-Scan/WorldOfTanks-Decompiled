# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/messenger/formatters/service_channel.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from helpers import dependency, int2roman
from messenger import g_settings
from messenger.formatters.service_channel import QuestAchievesFormatter, ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData
from shared_utils import first
from skeletons.gui.game_control import ITankAcademyController

class TankAcademyQuestAchievesFormatter(QuestAchievesFormatter):
    __tankAcademyController = dependency.descriptor(ITankAcademyController)

    @classmethod
    def _processTokens(cls, tokens):
        if cls.isWithSelectableReward(tokens):
            token = first((t for t in tokens.get('tokens').keys() if cls.__tankAcademyController.isTAOfferToken(t)))
            properties = cls.__tankAcademyController.getOfferProperties(token)
            if properties:
                level = properties.get('giftVehiclesLevel')
                isPremium = 'giftPremiumVehicles' in properties
                if level:
                    tokenTextResource = R.strings.tank_academy.serviceChannelMessages.token
                    return text_styles.stats(backport.text(tokenTextResource.premium() if isPremium else tokenTextResource(), level=int2roman(int(level))))

    @classmethod
    def isWithSelectableReward(cls, awardsDict):
        return False if 'tokens' not in awardsDict else any((cls.__tankAcademyController.isTAOfferToken(v) for v in awardsDict['tokens'].iterkeys()))


class TankAcademyTokenAward(ServiceChannelFormatter):
    __TEMPLATE = 'TankAcademyTokenAward'

    def format(self, message, *args):
        achievesFormatter = TankAcademyQuestAchievesFormatter()
        achieves = achievesFormatter.formatQuestAchieves(message, asBattleFormatter=False)
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE, {'achieves': achieves})
        settings = self._getGuiSettings(message, self.__TEMPLATE)
        return [MessageData(formatted, settings)]
