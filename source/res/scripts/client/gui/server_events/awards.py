# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/awards.py
from collections import namedtuple
import BigWorld
import constants
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
import potapov_quests
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers import i18n
from shared_utils import findFirst
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.AwardWindow import AwardAbstract, ExplosionBackAward, packRibbonInfo, MissionAwardAbstract
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters import text_styles
from gui.shared.utils.decorators import process
from skeletons.gui.server_events import IEventsCache

def _getNextQuestInTileByID(questID):
    eventsCache = dependency.instance(IEventsCache)
    quests = eventsCache.potapov.getQuests()
    questsInTile = sorted(potapov_quests.g_cache.questListByTileIDChainID(quests[questID].getTileID(), quests[questID].getChainID()))
    try:
        questInd = questsInTile.index(questID)
        for nextID in questsInTile[questInd + 1:]:
            if quests[nextID].isAvailableToPerform():
                return nextID

        for nextID in questsInTile[:questInd + 1]:
            if quests[nextID].isAvailableToPerform():
                return nextID

    except ValueError:
        LOG_ERROR('Cannot find quest ID {questID} in quests from tile {quests}'.format(questID=questID, quests=questsInTile))
        LOG_CURRENT_EXCEPTION()

    return None


class AchievementsAward(AwardAbstract):

    def __init__(self, achieves):
        assert hasattr(achieves, '__iter__')
        self.__achieves = achieves

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_NEWMEDALS)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARD_CREDITS_GLOW

    def getHeader(self):
        return text_styles.highTitle(i18n.makeString(MENU.AWARDWINDOW_QUESTS_MEDALS_HEADER))

    def getDescription(self):
        descr = []
        for achieve in self.__achieves:
            noteInfo = achieve.getNotificationInfo()
            if len(noteInfo):
                descr.append(noteInfo)

        return text_styles.main('\n\n'.join(descr))

    def getExtraFields(self):
        result = []
        for a in self.__achieves:
            result.append({'type': a.getRecordName()[1],
             'block': a.getBlock(),
             'icon': {'big': a.getBigIcon(),
                      'small': a.getSmallIcon()}})

        return {'achievements': result}


class TokenAward(ExplosionBackAward):

    def __init__(self, potapovQuest, tokenID, count, proxyEvent):
        super(TokenAward, self).__init__()
        self.__potapovQuest = potapovQuest
        self.__tokenID = tokenID
        self.__tokenCount = count
        self.__proxyEvent = proxyEvent

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_TOKENS)

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_QUESTS_TOKEN256

    def getHeader(self):
        return text_styles.highTitle(i18n.makeString(MENU.AWARDWINDOW_QUESTS_TOKENS_HEADER, count=self.__tokenCount))

    def getDescription(self):
        return text_styles.main(i18n.makeString(MENU.AWARDWINDOW_QUESTS_TOKENS_DESCRIPTION))

    def handleBodyButton(self):
        nextQuestID = _getNextQuestInTileByID(int(self.__potapovQuest.getID()))
        if nextQuestID is not None:
            self.__proxyEvent(nextQuestID, constants.EVENT_TYPE.POTAPOV_QUEST)
        return

    def getBodyButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_TAKENEXTBUTTON)

    def getButtonStates(self):
        if not self.__potapovQuest.isFinal():
            return super(TokenAward, self).getButtonStates()
        else:
            nextQuestID = _getNextQuestInTileByID(int(self.__potapovQuest.getID()))
            return (False, True, nextQuestID is not None)
            return None


class VehicleAward(ExplosionBackAward):

    def __init__(self, vehicle):
        super(VehicleAward, self).__init__()
        self.__vehicle = vehicle

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_NEWVEHICLE)

    def getAwardImage(self):
        return self.__vehicle.iconUniqueLight

    def getHeader(self):
        return text_styles.highTitle(i18n.makeString(MENU.AWARDWINDOW_QUESTS_VEHICLE_HEADER, vehicleName=self.__vehicle.userName))

    def getDescription(self):
        return text_styles.main(i18n.makeString(MENU.AWARDWINDOW_QUESTS_VEHICLE_DESCRIPTION))


class TankwomanAward(ExplosionBackAward):

    def __init__(self, questID, tankmanData, proxyEvent):
        super(TankwomanAward, self).__init__()
        self.__questID = questID
        self.__tankmanData = tankmanData
        self.__proxyEvent = proxyEvent

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_NEWTANKMAN)

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_QUESTS_TANKMANFEMALEORANGE

    def getHeader(self):
        return text_styles.highTitle(i18n.makeString(MENU.AWARDWINDOW_QUESTS_TANKMANFEMALE_HEADER))

    def getDescription(self):
        return text_styles.main(i18n.makeString(MENU.AWARDWINDOW_QUESTS_TANKMANFEMALE_DESCRIPTION))

    def getOkButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_RECRUITBUTTON)

    def handleOkButton(self):
        self.__proxyEvent(self.__questID, self.__tankmanData.isPremium, self.__tankmanData.fnGroupID, self.__tankmanData.lnGroupID, self.__tankmanData.iGroupID)


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
            return [self._BonusFmt(self._icon, BigWorld.wg_getIntegralFormat(bonus.getValue()), self._tooltip, None)]

    class _SimpleNoValueFormatter(_SimpleFormatter):

        def __call__(self, bonus):
            return [self._BonusFmt(self._icon, '', self._tooltip, None)]

    class _ItemsFormatter(_BonusFormatter):

        def __call__(self, bonus):
            result = []
            for item, count in bonus.getItems().iteritems():
                if item is not None and count:
                    tooltip = makeTooltip(header=item.userName, body=item.fullDescription)
                    result.append(self._BonusFmt(item.icon, BigWorld.wg_getIntegralFormat(count), tooltip, None))

            return result

    class _BoostersFormatter(_BonusFormatter):

        def __call__(self, bonus):
            result = []
            for booster, count in bonus.getBoosters().iteritems():
                if booster is not None and count:
                    tooltip = TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO
                    result.append(self._BonusFmt('', BigWorld.wg_getIntegralFormat(count), tooltip, self.__makeBoosterVO(booster)))

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
        self._formatters = {'gold': self._SimpleFormatter(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICONBIG, tooltip=TOOLTIPS.AWARDITEM_GOLD),
         'credits': self._SimpleFormatter(RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICONBIG_1, tooltip=TOOLTIPS.AWARDITEM_CREDITS),
         'freeXP': self._SimpleFormatter(RES_ICONS.MAPS_ICONS_LIBRARY_FREEXPICONBIG, tooltip=TOOLTIPS.AWARDITEM_FREEXP),
         'premium': self._SimpleNoValueFormatter(RES_ICONS.MAPS_ICONS_LIBRARY_PREMDAYICONBIG, tooltip=TOOLTIPS.AWARDITEM_PREMIUM),
         'items': self._ItemsFormatter(),
         'goodies': self._BoostersFormatter()}

    def clear(self):
        self._formatters.clear()

    def getRibbonInfo(self):
        awards, strAwards = self._getMainAwards(self._getBonuses())
        return packRibbonInfo(awardForCompleteText=i18n.makeString(MENU.AWARDWINDOW_QUESTS_TASKCOMPLETE_AWARDFORCOMLETE), awardBonusStrText=strAwards, awards=awards) if strAwards or awards else None

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

        if len(strAwardsList):
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
        return i18n.makeString('#tutorial:tutorialQuest/awardWindow/title')

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_HANGARTUTORIAL_GOALSQUEST

    def getHeader(self):
        return i18n.makeString('#tutorial:tutorialQuest/awardWindow/header', qName=i18n.makeString(self.__quest.getUserName()))

    def getDescription(self):
        return self.__quest.getAwardMsg()

    def getBodyButtonText(self):
        return i18n.makeString('#tutorial:tutorialQuest/awardWindow/nextQuest')

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
            self.__proxyEvent(nextQuest.getID(), constants.EVENT_TYPE.MOTIVE_QUEST)
        return


class MissionAward(MissionAwardAbstract):

    def __init__(self, quest, ctx, proxyEvent):
        super(MissionAward, self).__init__()
        self._quest = quest
        self._eventsCache = ctx['eventsCache']
        self._proxyEvent = proxyEvent

    def getWindowTitle(self):
        return i18n.makeString('#menu:awardWindow/title/taskComplete')

    def getBackgroundImage(self):
        pass

    def getRibbonImage(self):
        pass

    def getDescription(self):
        return text_styles.promoTitle('#menu:awardWindow/mission/complete')

    def getCurrentQuestHeader(self):
        return text_styles.highTitle(self._quest.getUserName())

    def getCurrentQuestConditions(self):
        return {'containerElements': events_helpers.getEventConditions(self._quest)}

    def getMainStatusText(self):
        return text_styles.success('#menu:awardWindow/mission/conditionComplete')

    def getMainStatusIcon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_OKICON

    def getAvalableText(self):
        count = text_styles.neutral(self.__getMissionsCount())
        return text_styles.standard(i18n.makeString('#menu:awardWindow/mission/available', count=count))

    def getNextButtonText(self):
        return i18n.makeString('#menu:awardWindow/mission/nextButton')

    def getNextButtonTooltip(self):
        return makeTooltip('#menu:awardWindow/mission/nextButton/tooltip/header', '#menu:awardWindow/mission/nextButton/tooltip/body')

    def isNextAvailable(self):
        return self.__getMissionsCount() != 0

    def isLast(self):
        return not self.isNextAvailable()

    def getAwards(self):
        return events_helpers.getCarouselAwardVO(self._quest.getBonuses(), isReceived=True)

    def handleNextButton(self):
        self._proxyEvent(eventType=constants.EVENT_TYPE.BATTLE_QUEST)

    def __getMissionsCount(self):
        return len(self._eventsCache.getQuests(lambda q: q.isAvailable()[0] and q.getType() not in constants.EVENT_TYPE.SHARED_QUESTS and not q.isCompleted()))


class PersonalMissionAward(MissionAward):

    def __init__(self, quest, ctx, proxyEvent):
        super(PersonalMissionAward, self).__init__(quest, ctx, proxyEvent)
        nextQuestID = _getNextQuestInTileByID(int(self._quest.getID()))
        if nextQuestID is not None and not self._quest.isFinal():
            self._nextQuest = self._eventsCache.potapov.getQuests()[nextQuestID]
        else:
            self._nextQuest = None
        self._tile = self._eventsCache.potapov.getTiles()[self._quest.getTileID()]
        self._isAddReward = ctx.get('isAddReward', False)
        self._isMainReward = ctx.get('isMainReward', False)
        return

    def getBackgroundImage(self):
        return '../maps/icons/quests/awards/tile_{}_{}_award_bg.png'.format(self._tile.getSeasonID(), self._tile.getID())

    def getHeader(self):
        return text_styles.stats(i18n.makeString('#quests:tileChainsView/title', name=self._tile.getUserName()))

    def getDescription(self):
        if self._isAddReward:
            key = '#menu:awardWindow/personalMission/completeWithHonors'
        else:
            key = '#menu:awardWindow/personalMission/complete'
        return text_styles.promoTitle(key)

    def getCurrentQuestConditionsText(self):
        return self._quest.getUserMainCondition()

    def getCurrentQuestConditions(self):
        return None

    def getMainStatusText(self):
        statusText = text_styles.success('#menu:awardWindow/mission/mainConditionComplete')
        if not self._isMainReward:
            return text_styles.concatStylesWithSpace(statusText, text_styles.standard('#menu:awardWindow/personalMission/alreadyCompleted'))
        else:
            return statusText

    def getAdditionalStatusText(self):
        if self._isAddReward:
            return text_styles.success('#menu:awardWindow/personalMission/sideConditionCompleted')
        else:
            return text_styles.neutral('#menu:awardWindow/personalMission/sideConditionNotCompleted')

    def getAdditionalStatusIcon(self):
        if self._isAddReward:
            return RES_ICONS.MAPS_ICONS_LIBRARY_OKICON
        else:
            return ''

    def getNextQuestHeader(self):
        if self._nextQuest is not None:
            return text_styles.highTitle(self._nextQuest.getUserName())
        else:
            return ''
            return

    def getNextQuestConditions(self):
        if self._nextQuest is not None:
            return self._nextQuest.getUserMainCondition()
        else:
            return ''
            return

    def getAvalableText(self):
        return text_styles.standard('#menu:awardWindow/personalMission/available')

    def getAwards(self):
        bonuses = []
        if self._isMainReward:
            bonuses.extend(self._quest.getBonuses(isMain=True))
        if self._isAddReward:
            bonuses.extend(self._quest.getBonuses(isMain=False))
        return events_helpers.getCarouselAwardVO(bonuses, isReceived=True)

    def getNextButtonText(self):
        if self._quest.isFinal():
            return i18n.makeString('#menu:awardWindow/personalMission/nextButtonAward')
        else:
            return i18n.makeString('#menu:awardWindow/personalMission/nextButton')

    def isNextAvailable(self):
        return not self._quest.isFinal() and self._nextQuest is not None

    def isLast(self):
        return self._quest.isFinal() and self._quest.needToGetReward()

    def isPersonal(self):
        return True

    def getNextButtonTooltip(self):
        if self._quest.isFinal():
            return makeTooltip('#menu:awardWindow/personalMission/nextButtonAward/tooltip/header', '#menu:awardWindow/personalMission/nextButtonAward/tooltip/body')
        else:
            return makeTooltip('#menu:awardWindow/personalMission/nextButton/tooltip/header', '#menu:awardWindow/personalMission/nextButton/tooltip/body')

    def handleNextButton(self):
        if self._nextQuest is not None:
            self._proxyEvent(eventID=self._nextQuest.getID(), eventType=constants.EVENT_TYPE.POTAPOV_QUEST)
        else:
            self.__tryGetAward()
        return

    def handleCurrentButton(self):
        self._proxyEvent(eventID=self._quest.getID(), eventType=constants.EVENT_TYPE.POTAPOV_QUEST)

    @process('updating')
    def __tryGetAward(self):
        result = yield events_helpers.getPotapovQuestAward(self._quest)
        if result and len(result.userMsg):
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
