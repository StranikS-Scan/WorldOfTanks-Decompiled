# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/awards.py
from collections import namedtuple
import constants
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData, getAwardsWindowBonuses, getEpicAwardsWindowBonuses
from gui.Scaleform.genConsts.AWARDWINDOW_CONSTANTS import AWARDWINDOW_CONSTANTS
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip, stripColorTagDescrTags
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.shared_components import i18n
from shared_utils import findFirst
from skeletons.gui.server_events import IEventsCache
AwardsRibbonInfo = namedtuple('AwardsRibbonInfo', ['awardForCompleteText',
 'isAwardForCompleteVisible',
 'awardReceivedText',
 'isAwardsReceivedVisible',
 'awardBonusStrText',
 'isAwardBonusStrVisible',
 'ribbonSource',
 'awards'])

def packRibbonInfo(awards=None, awardForCompleteText='', awardReceivedText='', awardBonusStrText=''):
    return AwardsRibbonInfo(awardForCompleteText=awardForCompleteText, isAwardForCompleteVisible=bool(len(awardForCompleteText)), awardReceivedText=awardReceivedText, isAwardsReceivedVisible=bool(len(awardReceivedText)), awardBonusStrText=awardBonusStrText, isAwardBonusStrVisible=bool(len(awardBonusStrText)), ribbonSource=RES_ICONS.MAPS_ICONS_QUESTS_AWARDRIBBON, awards=awards or [])


class AwardAbstract(object):

    def getWindowTitle(self):
        pass

    def getBackgroundImage(self):
        pass

    def useBackgroundAnimation(self):
        return False

    def getBackgroundAnimationData(self):
        return None

    def getAwardImage(self):
        return None

    def getHeader(self):
        pass

    def getDescription(self):
        pass

    def getAdditionalText(self):
        pass

    def getTextAreaIconPath(self):
        pass

    def getTextAreaIconIsShow(self):
        return False

    def getExtraFields(self):
        return {}

    def getHasDashedLine(self):
        return False

    def getButtonStates(self):
        return (True, False, False)

    def getOkButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_OKBUTTON)

    def getCloseButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_CLOSEBUTTON)

    def getBodyButtonText(self):
        pass

    def getBodyButtonLinkage(self):
        return AWARDWINDOW_CONSTANTS.BODY_BUTTON_LINKAGE_DEFAULT

    def getRibbonInfo(self):
        return None

    def handleOkButton(self):
        pass

    def handleCloseButton(self):
        pass

    def handleBodyButton(self):
        pass

    def clear(self):
        pass

    def getSound(self):
        return None


class MissionAwardAbstract(AwardAbstract):

    def getRibbonImage(self):
        pass

    def getCurrentQuestHeader(self):
        pass

    def getCurrentQuestConditions(self):
        return []

    def getNextQuestHeader(self):
        pass

    def getNextQuestConditions(self):
        return []

    def getNextQuestConditionsHeader(self):
        pass

    def getAdditionalStatusText(self):
        pass

    def getMainStatusText(self):
        pass

    def getMainStatusIcon(self):
        pass

    def getAvailableText(self):
        pass

    def getAdditionalStatusIcon(self):
        pass

    def getNextButtonText(self):
        pass

    def getNextButtonTooltip(self):
        pass

    def isNextAvailable(self):
        return False

    def isLast(self):
        return False

    def isPersonal(self):
        return False

    def getAwards(self):
        return []

    def handleNextButton(self):
        pass

    def handleCurrentButton(self):
        pass


class ExplosionBackAward(AwardAbstract):

    def __init__(self, useAnimation=True):
        super(ExplosionBackAward, self).__init__()
        self.__useAnimation = useAnimation

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def useBackgroundAnimation(self):
        return self.__useAnimation

    def getBackgroundAnimationData(self):
        return {'image': self.getAwardImage(),
         'animationPath': AWARDWINDOW_CONSTANTS.EXPLOSION_BACK_ANIMATION_PATH,
         'animationLinkage': AWARDWINDOW_CONSTANTS.EXPLOSION_BACK_ANIMATION_LINKAGE} if self.__useAnimation else None


class AchievementsAward(AwardAbstract):

    def __init__(self, achieves):
        if not hasattr(achieves, '__iter__'):
            raise UserWarning('Received argument is not iterable', achieves)
        self.__achieves = achieves

    def getWindowTitle(self):
        return _ms(MENU.AWARDWINDOW_TITLE_NEWMEDALS)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARD_CREDITS_GLOW

    def getHeader(self):
        return text_styles.highTitle(_ms(MENU.AWARDWINDOW_QUESTS_MEDALS_HEADER))

    def getDescription(self):
        descr = []
        for achieve in self.__achieves:
            noteInfo = achieve.getNotificationInfo()
            if noteInfo:
                descr.append(noteInfo)

        return text_styles.main('\n\n'.join(descr))

    def getExtraFields(self):
        result = []
        for a in self.__achieves:
            result.append({'type': a.getRecordName()[1],
             'block': a.getBlock(),
             'rank': a.getValue(),
             'icon': {'big': a.getHugeIcon(),
                      'small': a.getSmallIcon()}})

        return {'achievements': result}


class FormattedAward(AwardAbstract):

    class _BonusFormatter(object):
        _BonusFmt = namedtuple('_BonusFmt', 'icon value tooltip bonusVO')

        def __call__(self, bonus):
            return []

    class _SimpleFormatter(_BonusFormatter):

        def __init__(self, icon, tooltip=''):
            self._icon = icon
            self._tooltip = tooltip

        def __call__(self, bonus):
            return [self._BonusFmt(self._icon, backport.getIntegralFormat(bonus.getValue()), self._tooltip, None)]

    class _SimpleNoValueFormatter(_SimpleFormatter):

        def __call__(self, bonus):
            return [self._BonusFmt(self._icon, '', self._tooltip, None)]

    class _ItemsFormatter(_BonusFormatter):

        def __call__(self, bonus):
            result = []
            for item, count in bonus.getItems().iteritems():
                if item is not None and count:
                    description = item.fullDescription
                    if item.itemTypeID in (GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.EQUIPMENT):
                        description = stripColorTagDescrTags(description)
                    tooltip = makeTooltip(header=item.userName, body=description)
                    result.append(self._BonusFmt(item.icon, backport.getIntegralFormat(count), tooltip, None))

            return result

    class _BoostersFormatter(_BonusFormatter):

        def __call__(self, bonus):
            result = []
            for booster, count in bonus.getBoosters().iteritems():
                if booster is not None and count:
                    tooltip = TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO
                    result.append(self._BonusFmt('', backport.getIntegralFormat(count), tooltip, self.__makeBoosterVO(booster)))

            return result

        @staticmethod
        def __makeBoosterVO(booster):
            return {'icon': booster.icon,
             'showCount': False,
             'qualityIconSrc': booster.getQualityIcon(),
             'slotLinkage': BOOSTER_CONSTANTS.SLOT_UI,
             'showLeftTime': False,
             'boosterId': booster.boosterID}

    def __init__(self):
        self._formatters = {Currency.GOLD: self._SimpleFormatter(RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_GOLD, tooltip=TOOLTIPS.AWARDITEM_GOLD),
         Currency.CREDITS: self._SimpleFormatter(RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_CREDITS, tooltip=TOOLTIPS.AWARDITEM_CREDITS),
         Currency.CRYSTAL: self._SimpleFormatter(RES_ICONS.MAPS_ICONS_LIBRARY_CRYSTALICONBIG_1, tooltip=TOOLTIPS.AWARDITEM_CRYSTAL),
         'freeXP': self._SimpleFormatter(RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_FREEEXP, tooltip=TOOLTIPS.AWARDITEM_FREEXP),
         'premium': self._SimpleNoValueFormatter(RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_PREMIUM_1, tooltip=TOOLTIPS.AWARDITEM_PREMIUM),
         'items': self._ItemsFormatter(),
         'goodies': self._BoostersFormatter()}

    def clear(self):
        self._formatters.clear()

    def getRibbonInfo(self):
        awards, strAwards = self._getMainAwards(self._getBonuses())
        return packRibbonInfo(awardForCompleteText=_ms(MENU.AWARDWINDOW_QUESTS_TASKCOMPLETE_AWARDFORCOMLETE), awardBonusStrText=strAwards, awards=awards) if strAwards or awards else None

    def _getBonuses(self):
        return []

    def _getMainAwards(self, bonuses):
        awards = []
        strAwardsList = []
        strAwards = ''
        for b in bonuses:
            formatter = self._formatters.get(b.getName(), None)
            if callable(formatter):
                for bonus in formatter(b):
                    awards.append({'value': bonus.value,
                     'itemSource': bonus.icon,
                     'tooltip': bonus.tooltip,
                     'boosterVO': bonus.bonusVO})

            formattedBonus = b.format()
            if formattedBonus:
                strAwardsList.append(text_styles.warning(formattedBonus))

        if strAwardsList:
            strAwards = ', '.join(strAwardsList)
        return (awards, strAwards)


class MotiveQuestAward(FormattedAward):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, motiveQuest, proxyEvent):
        super(MotiveQuestAward, self).__init__()
        self.__quest = motiveQuest
        self.__proxyEvent = proxyEvent

    def clear(self):
        super(MotiveQuestAward, self).clear()
        self.__quest = None
        return

    def getButtonStates(self):
        return (False, True, self.__getNextMotiveQuest() is not None)

    def getWindowTitle(self):
        return _ms('#tutorial:tutorialQuest/awardWindow/title')

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_HANGARTUTORIAL_GOALSQUEST

    def getHeader(self):
        return _ms('#tutorial:tutorialQuest/awardWindow/header', qName=_ms(self.__quest.getUserName()))

    def getDescription(self):
        return self.__quest.getAwardMsg()

    def getBodyButtonText(self):
        return _ms('#tutorial:tutorialQuest/awardWindow/nextQuest')

    def _getBonuses(self):
        return self.__quest.getBonuses()

    def __getNextMotiveQuest(self):
        quests = self.eventsCache.getMotiveQuests(lambda q: q.isAvailable() and not q.isCompleted())
        sortedQuests = sorted(quests.values(), key=lambda q: q.getPriority())
        nextQuest = findFirst(None, sortedQuests)
        for quest in sortedQuests:
            if quest.getPriority() > self.__quest.getPriority():
                return quest

        return nextQuest

    def handleBodyButton(self):
        nextQuest = self.__getNextMotiveQuest()
        if nextQuest is not None:
            self.__proxyEvent(nextQuest.getID())
        return


class MissionAward(MissionAwardAbstract):

    def __init__(self, quest, ctx, proxyEvent):
        super(MissionAward, self).__init__()
        self._quest = quest
        self._eventsCache = ctx['eventsCache']
        self._proxyEvent = proxyEvent

    def getWindowTitle(self):
        return _ms('#menu:awardWindow/title/taskComplete')

    def getBackgroundImage(self):
        pass

    def getRibbonImage(self):
        pass

    def getDescription(self):
        return text_styles.promoTitle('#menu:awardWindow/mission/complete')

    def getCurrentQuestHeader(self):
        return text_styles.highTitle(self._quest.getUserName())

    def getMainStatusText(self):
        return text_styles.success('#menu:awardWindow/mission/conditionComplete')

    def getMainStatusIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_OKICON

    def getAvailableText(self):
        count = text_styles.neutral(self.__getMissionsCount())
        return text_styles.standard(_ms('#menu:awardWindow/mission/available', count=count))

    def getNextButtonText(self):
        return _ms('#menu:awardWindow/mission/nextButton')

    def getNextButtonTooltip(self):
        return makeTooltip('#menu:awardWindow/mission/nextButton/tooltip/header', '#menu:awardWindow/mission/nextButton/tooltip/body')

    def isNextAvailable(self):
        return self.__getMissionsCount() != 0

    def isLast(self):
        return not self.isNextAvailable()

    def getAwards(self):
        bonuses = getMissionInfoData(self._quest).getSubstituteBonuses()
        return getAwardsWindowBonuses(bonuses)

    def handleNextButton(self):
        self._proxyEvent()

    def __getMissionsCount(self):
        return len(self._eventsCache.getQuests(lambda q: q.isAvailable()[0] and q.getType() not in constants.EVENT_TYPE.SHARED_QUESTS and not q.isCompleted()))


class OperationUnlockedAward(MissionAward):
    BODY_BUTTON_LINKAGE = 'LobbyMenuButton'

    def __init__(self, quest, ctx, proxyEvent):
        super(OperationUnlockedAward, self).__init__(quest, ctx, proxyEvent)
        _nextOperationID = ctx.get('nextOperationID', 1)
        self._nextOperation = self._eventsCache.getPersonalMissions().getAllOperations()[_nextOperationID]

    def isPersonal(self):
        return False

    def getWindowTitle(self):
        return _ms(PERSONAL_MISSIONS.OPERATIONUNLOCKEDWINDOW_TITLE)

    def getBackgroundImage(self):
        return '../maps/icons/quests/awards/operation_{}_award_bg.png'.format(self._nextOperation.getID())

    def getHeader(self):
        return text_styles.superPromoTitle(makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
         'message': _ms(PERSONAL_MISSIONS.OPERATIONUNLOCKEDWINDOW_HEADER, title=self._nextOperation.getShortUserName())}))

    def getDescription(self):
        pass

    def getAdditionalText(self):
        return text_styles.main(makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
         'message': _ms(PERSONAL_MISSIONS.OPERATIONUNLOCKEDWINDOW_DESCR, label=_ms(PERSONAL_MISSIONS.OPERATIONUNLOCKEDWINDOW_NEXTBUTTON))}))

    def getRibbonInfo(self):
        return packRibbonInfo(awardReceivedText=text_styles.highlightText(_ms(PERSONAL_MISSIONS.OPERATIONUNLOCKEDWINDOW_AWARDTEXT, title=self._nextOperation.getShortUserName())))

    def getButtonStates(self):
        return (False, False, True)

    def getBodyButtonLinkage(self):
        return self.BODY_BUTTON_LINKAGE

    def getBodyButtonText(self):
        return _ms(PERSONAL_MISSIONS.OPERATIONUNLOCKEDWINDOW_NEXTBUTTON)

    def handleBodyButton(self):
        self._proxyEvent(self._nextOperation.getID(), 1)


class EpicAward(MissionAward):

    def getAwards(self):
        bonuses = getMissionInfoData(self._quest).getSubstituteBonuses()
        return getEpicAwardsWindowBonuses(bonuses)
