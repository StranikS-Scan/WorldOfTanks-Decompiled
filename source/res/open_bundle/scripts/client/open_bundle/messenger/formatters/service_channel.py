# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/messenger/formatters/service_channel.py
from __future__ import absolute_import
from future.utils import viewitems
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.recruit_helper import getRecruitInfo
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from messenger import g_settings
from messenger.formatters.service_channel import QuestAchievesFormatter

class OpenBundleAchievesFormatter(QuestAchievesFormatter):
    _BULLET = u'\u2022'

    @classmethod
    def formatData(cls, data):
        if not data:
            return ''
        result = []
        fixedRewards = g_settings.htmlTemplates.format('openBundleFixedReward', {'text': cls.formatQuestAchieves(data.get('fixedBonus') or {})})
        randomBonus = cls.formatQuestAchieves(data.get('randomBonus') or {})
        cellRewards = g_settings.htmlTemplates.format('openBundleCellRewards', {'text': randomBonus}) if randomBonus else ''
        for rewardsType in (fixedRewards, cellRewards):
            if rewardsType:
                result.append(rewardsType)

        result.append('')
        return cls._SEPARATOR.join(result)

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter=False, processCustomizations=True, processTokens=True):
        result = cls.getFormattedAchieves(data, asBattleFormatter, processCustomizations, processTokens)
        if result:
            result = [ '{} {}'.format(cls._BULLET, s[len(cls._SEPARATOR):] if s.startswith(cls._SEPARATOR) else s) for s in result ]
            return cls._SEPARATOR.join(result)
        else:
            return None

    @classmethod
    def _processTokens(cls, tokens):
        result = []
        for token, tokenData in viewitems(tokens.get('tokens', {})):
            tankmanTokenResult = cls._processTankmanToken(token, tokenData)
            if tankmanTokenResult:
                result.append(tankmanTokenResult)

        return '{}{} '.format(cls._SEPARATOR, cls._BULLET).join(result)

    @classmethod
    def _processTankmanToken(cls, tokenName, tokenData):
        if tokenName.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
            tankmanInfo = getRecruitInfo(tokenName)
            if tankmanInfo is not None:
                groupName = tankmanInfo.getGroupName()
                if groupName == 'men1':
                    text = backport.text(R.strings.open_bundle.formatter.crew.male(), count=str(tokenData.get('count')))
                elif groupName == 'women1':
                    text = backport.text(R.strings.open_bundle.formatter.crew.female(), count=str(tokenData.get('count')))
                else:
                    text = backport.text(R.strings.open_bundle.formatter.uniqueTankman(), fullName=tankmanInfo.getFullUserName())
                return g_settings.htmlTemplates.format('openBundleTankman', {'text': text})
        return
