# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/messenger/formatters/token_quest_subformatters.py
from adisp import adisp_async, adisp_process
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from helpers import dependency, int2roman
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData
from messenger.formatters.token_quest_subformatters import TokenQuestsSubFormatter, AsyncTokenQuestsSubFormatter
from shared_utils import first
from skeletons.gui.game_control import ITankAcademyController
from tank_academy.gui.server_events.events_helpers import parseTankAcademyQuestID
from tank_academy.notification.decorators import TankAcademyAwardsDecorator
from tank_academy.messenger.formatters.service_channel import TankAcademyQuestAchievesFormatter

class TankAcademyAwardsFormatterBase(ServiceChannelFormatter, TokenQuestsSubFormatter):
    __tankAcademyController = dependency.descriptor(ITankAcademyController)
    __MESSAGE_TEMPLATE = 'TankAcademy{}'
    __TOKEN_TYPE = 'TokenQuest'
    __AWARD_TYPE = 'AwardsQuest'

    def __init__(self):
        super(TankAcademyAwardsFormatterBase, self).__init__()
        self._achievesFormatter = TankAcademyQuestAchievesFormatter()

    def _format(self, message, *args):
        messageDataList = []
        data = message.data or {}
        completedQuestIDs = sorted(self.getQuestOfThisGroup(data.get('completedQuestIDs', set())), key=lambda q: parseTankAcademyQuestID(q)[0])
        for qID in completedQuestIDs:
            messageData = self.__buildMessage(qID, message)
            if messageData is not None:
                messageDataList.append(messageData)

        return messageDataList if messageDataList else [MessageData(None, None)]

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return cls.__tankAcademyController.isTankAcademyQuestID(questID)

    def __buildMessage(self, questID, message):
        data = message.data or {}
        rewards = data.get('detailedRewards', {}).get(questID, {})
        isWithSelectableReward = self._achievesFormatter.isWithSelectableReward(rewards)
        fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False)
        if fmt is not None:
            questIdx, _ = parseTankAcademyQuestID(questID)
            finalQuest = self.__tankAcademyController.getFinalQuest()
            if finalQuest and finalQuest.getID() == questID:
                body = backport.text(R.strings.tank_academy.serviceChannelMessages.awards.done.body())
            else:
                body = backport.text(R.strings.tank_academy.serviceChannelMessages.awards.body(), questIdx=text_styles.stats(str(questIdx)))
            rewardToken = first([ k for k in rewards.get('tokens', {}) if self.__tankAcademyController.isTAOfferToken(k) ])
            templateParams = {'achieves': fmt or '',
             'body': body}
            if isWithSelectableReward:
                template = self.__MESSAGE_TEMPLATE.format(self.__TOKEN_TYPE)
                properties = self.__tankAcademyController.getOfferProperties(rewardToken)
                if properties:
                    level = properties.get('giftVehiclesLevel')
                    isPremium = 'giftPremiumVehicles' in properties
                    footerTextResource = R.strings.tank_academy.serviceChannelMessages.awards.footer
                    footer = backport.text(footerTextResource.premium() if isPremium else footerTextResource(), level=int2roman(int(level)))
                    templateParams['footer'] = footer
            else:
                template = self.__MESSAGE_TEMPLATE.format(self.__AWARD_TYPE)
            settings = self._getGuiSettings(message, template, decorator=TankAcademyAwardsDecorator, auxData={'questID': questID,
             'isWithSelectableReward': isWithSelectableReward})
            formatted = g_settings.msgTemplates.format(template, ctx=templateParams, data={'savedData': {'rewardToken': rewardToken}})
            return MessageData(formatted, settings)
        else:
            return


class TankAcademyAwardsFormatter(AsyncTokenQuestsSubFormatter, TankAcademyAwardsFormatterBase):

    def __init__(self):
        AsyncTokenQuestsSubFormatter.__init__(self)
        TankAcademyAwardsFormatterBase.__init__(self)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            messageDataList = self._format(message)
        if messageDataList:
            callback(messageDataList)
        callback([MessageData(None, None)])
        return


class TankAcademyClientAwardsFormatter(TankAcademyAwardsFormatterBase):

    def format(self, message, *args):
        return self._format(message, *args)
