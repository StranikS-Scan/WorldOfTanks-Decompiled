# Embedded file name: scripts/client/gui/server_events/awards.py
import random
from collections import namedtuple
import BigWorld
import constants
from helpers import i18n
from gui.shared.utils import findFirst
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.lobby.AwardWindow import AwardAbstract, packRibbonInfo
from gui.Scaleform.framework.managers.TextManager import TextType

class AchievementsAward(AwardAbstract):

    def __init__(self, achieves):
        raise hasattr(achieves, '__iter__') or AssertionError
        self.__achieves = achieves

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_NEWMEDALS)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARD_CREDITS_GLOW

    def getHeader(self):
        return self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, i18n.makeString(MENU.AWARDWINDOW_QUESTS_MEDALS_HEADER))

    def getDescription(self):
        descr = []
        for achieve in self.__achieves:
            noteInfo = achieve.getNotificationInfo()
            if len(noteInfo):
                descr.append(noteInfo)

        return self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, '\n\n'.join(descr))

    def getExtraFields(self):
        result = []
        for a in self.__achieves:
            result.append({'type': a.getRecordName()[1],
             'block': a.getBlock(),
             'icon': {'big': a.getBigIcon(),
                      'small': a.getSmallIcon()}})

        return {'achievements': result}


class TokensAward(AwardAbstract):

    def __init__(self, tokens):
        raise hasattr(tokens, '__iter__') or AssertionError
        self.__tokens = tokens

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_TOKENS)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_QUESTS_TOKEN256

    def getHeader(self):
        return self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, i18n.makeString(MENU.AWARDWINDOW_QUESTS_TOKENS_HEADER, count=self.__getTotalTokensCount()))

    def getDescription(self):
        return self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(MENU.AWARDWINDOW_QUESTS_TOKENS_DESCRIPTION))

    def __getTotalTokensCount(self):
        return sum(self.__tokens.values())


class VehicleAward(AwardAbstract):

    def __init__(self, vehicle):
        self.__vehicle = vehicle

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_NEWVEHICLE)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return self.__vehicle.iconUniqueLight

    def getHeader(self):
        return self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, i18n.makeString(MENU.AWARDWINDOW_QUESTS_VEHICLE_HEADER, vehicleName=self.__vehicle.userName))

    def getDescription(self):
        return self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(MENU.AWARDWINDOW_QUESTS_VEHICLE_DESCRIPTION))


class TankwomanAward(AwardAbstract):

    def __init__(self, questID, tankmanData):
        self.__questID = questID
        self.__tankmanData = tankmanData

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_NEWTANKMAN)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_QUESTS_TANKMANFEMALEORANGE

    def getHeader(self):
        return self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, i18n.makeString(MENU.AWARDWINDOW_QUESTS_TANKMANFEMALE_HEADER))

    def getDescription(self):
        return self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(MENU.AWARDWINDOW_QUESTS_TANKMANFEMALE_DESCRIPTION))

    def getOkButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_RECRUITBUTTON)

    def handleOkButton(self):
        from gui.server_events import events_dispatcher as quests_events
        quests_events.showTankwomanRecruitWindow(self.__questID, self.__tankmanData.isPremium, self.__tankmanData.fnGroupID, self.__tankmanData.lnGroupID, self.__tankmanData.iGroupID)


class RegularAward(AwardAbstract):
    _BG_IMG_BY_VEH_TYPE = {'lightTank': RES_ICONS.MAPS_ICONS_QUESTS_LTAWARDBACK,
     'mediumTank': RES_ICONS.MAPS_ICONS_QUESTS_MTAWARDBACK,
     'heavyTank': RES_ICONS.MAPS_ICONS_QUESTS_HTAWARDBACK,
     'AT-SPG': RES_ICONS.MAPS_ICONS_QUESTS_AT_SPGAWARDBACK,
     'SPG': RES_ICONS.MAPS_ICONS_QUESTS_SPGAWARDBACK}

    class _BonusFormatter(object):
        _BonusFmt = namedtuple('_BonusFmt', 'icon value')

        def __call__(self, bonus):
            return []

    class _SimpleFormatter(_BonusFormatter):

        def __init__(self, icon):
            self.__icon = icon

        def __call__(self, bonus):
            return [self._BonusFmt(self.__icon, BigWorld.wg_getIntegralFormat(bonus.getValue()))]

    class _ItemsFormatter(_BonusFormatter):

        def __call__(self, bonus):
            result = []
            for item, count in bonus.getItems().iteritems():
                if item is not None and count:
                    result.append(self._BonusFmt(item.icon, BigWorld.wg_getIntegralFormat(count)))

            return result

    def __init__(self, potapovQuest, isMainReward = False, isAddReward = False):
        raise True in (isMainReward, isAddReward) or AssertionError
        self.__potapovQuest = potapovQuest
        self.__isMainReward = isMainReward
        self.__isAddReward = isAddReward
        self.__formatters = {'gold': self._SimpleFormatter(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICONBIG),
         'credits': self._SimpleFormatter(RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICONBIG_1),
         'freeXP': self._SimpleFormatter(RES_ICONS.MAPS_ICONS_LIBRARY_FREEXPICONBIG),
         'items': self._ItemsFormatter()}

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_TASKCOMPLETE)

    def getBackgroundImage(self):
        vehType = findFirst(None, self.__potapovQuest.getVehicleClasses())
        if vehType in self._BG_IMG_BY_VEH_TYPE:
            return self._BG_IMG_BY_VEH_TYPE[vehType]
        else:
            return random.choice(self._BG_IMG_BY_VEH_TYPE.values())

    def getAwardImage(self):
        return ''

    def getHeader(self):
        return i18n.makeString(MENU.AWARDWINDOW_QUESTS_TASKCOMPLETE_HEADER, taskName=self.__potapovQuest.getUserName())

    def getDescription(self):
        return i18n.makeString(MENU.AWARDWINDOW_QUESTS_TASKCOMPLETE_DESCRIPTION)

    def getAdditionalText(self):
        if self.__isAddReward:
            _getText = self.app.utilsManager.textManager.getText
            result = []
            for b in self.__potapovQuest.getBonuses(isMain=False):
                if b.isShowInGUI():
                    result.append(b.format())

            return _getText(TextType.MAIN_TEXT, i18n.makeString(MENU.AWARDWINDOW_QUESTS_TASKCOMPLETE_ADDITIONAL, award=', '.join(result)))
        else:
            return i18n.makeString(MENU.AWARDWINDOW_QUESTS_TASKCOMPLETE_ADDITIONALNOTCOMPLETE)

    def getButtonStates(self):
        return (False, True, True)

    def getBodyButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_TAKENEXTBUTTON)

    def getRibbonInfo(self):
        if self.__isMainReward:
            return packRibbonInfo(awardForCompleteText=i18n.makeString(MENU.AWARDWINDOW_QUESTS_TASKCOMPLETE_AWARDFORCOMLETE), awards=self.__getMainRewards())
        else:
            return packRibbonInfo(awardReceivedText=i18n.makeString(MENU.AWARDWINDOW_QUESTS_TASKCOMPLETE_AWARDRECIEVED))

    def handleBodyButton(self):
        from gui.server_events import events_dispatcher as quests_events
        quests_events.showEventsWindow(int(self.__potapovQuest.getID()) + 1, constants.EVENT_TYPE.POTAPOV_QUEST)

    def __getMainRewards(self):
        result = []
        for b in self.__potapovQuest.getBonuses(isMain=True):
            formatter = self.__formatters.get(b.getName(), lambda *args: [])
            for bonus in formatter(b):
                result.append({'itemSource': bonus.icon,
                 'value': bonus.value})

        return result
