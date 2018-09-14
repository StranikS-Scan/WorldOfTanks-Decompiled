# Embedded file name: scripts/client/gui/awards/special_achievement_awards.py
import constants
from debug_utils import LOG_ERROR
from gui.goodies.Booster import _BOOSTER_DESCRIPTION_LOCALE
from gui.shared import event_dispatcher
from gui.shared.formatters import text_styles
from gui.shared.formatters.ranges import toRomanRangeString
from helpers import i18n, int2roman
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.lobby.AwardWindow import AwardAbstract

class ResearchAward(AwardAbstract):

    def __init__(self, vehiclesCount, messageNumber):
        self.vehiclesCount = vehiclesCount
        self.messageNumber = messageNumber

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_SPECIALACHIEVEMENT)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_AWARDS_VEHICLESRESEARCH

    def getHeader(self):
        return text_styles.highTitle(i18n.makeString(MENU.AWARDWINDOW_SPECIALACHIEVEMENT_HEADER))

    def getDescription(self):
        return text_styles.main(i18n.makeString('#menu:awardWindow/specialAchievement/research/description%d' % self.messageNumber, vehiclesCount=self.vehiclesCount))


class VictoryAward(AwardAbstract):

    def __init__(self, victoriesCount, messageNumber):
        self.victoriesCount = victoriesCount
        self.messageNumber = messageNumber

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_SPECIALACHIEVEMENT)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_AWARDS_VICTORY

    def getHeader(self):
        return text_styles.highTitle(i18n.makeString(MENU.AWARDWINDOW_SPECIALACHIEVEMENT_HEADER))

    def getDescription(self):
        return text_styles.main(i18n.makeString('#menu:awardWindow/specialAchievement/victory/description%d' % self.messageNumber, victoriesCount=self.victoriesCount))


class BattleAward(AwardAbstract):

    def __init__(self, battlesCount, messageNumber):
        self.battlesCount = battlesCount
        self.messageNumber = messageNumber

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_SPECIALACHIEVEMENT)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_AWARDS_BATTLESWORDS

    def getHeader(self):
        return text_styles.highTitle(i18n.makeString(MENU.AWARDWINDOW_SPECIALACHIEVEMENT_HEADER))

    def getDescription(self):
        return text_styles.main(i18n.makeString('#menu:awardWindow/specialAchievement/battle/description%d' % self.messageNumber, battlesCount=self.battlesCount))


class PvEBattleAward(BattleAward):

    def getWindowTitle(self):
        return i18n.makeString('#menu:awardWindow/title/info')

    def getDescription(self):
        return text_styles.main(i18n.makeString('#menu:awardWindow/specialAchievement/pveBattle/description', battlesCount=self.battlesCount))

    def handleOkButton(self):
        event_dispatcher.runTutorialChain('PvE_Chain')

    def handleCloseButton(self):
        event_dispatcher.runTutorialChain('PvE_Chain')


class PremiumDiscountAward(AwardAbstract):

    def __init__(self, researchLvl, premiumPacket, discount):
        self.researchLvl = researchLvl
        self.premiumPacket = premiumPacket
        self.discount = discount

    def getWindowTitle(self):
        return i18n.makeString(MENU.PREMIUMCONGRATULATION_TITLE)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return '../maps/icons/windows/prem/icon_prem%s_256.png' % self.premiumPacket

    def getHeader(self):
        return text_styles.highTitle(MENU.PREMIUMCONGRATULATION_HEDER)

    def getBodyButtonText(self):
        return i18n.makeString(MENU.PREMIUMCONGRATULATION_BTNLABEL)

    def getCloseButtonText(self):
        return i18n.makeString(MENU.PREMIUMCONGRATULATION_CLOSEBTN)

    def getPercentDiscount(self):
        return '%d%%' % self.discount

    def getDuration(self):
        return i18n.makeString('#menu:premium/packet/days%s' % self.premiumPacket)

    def getDescription(self):
        return text_styles.main(i18n.makeString(MENU.PREMIUMCONGRATULATION_DESCRIPTION, level=int2roman(self.researchLvl), duration=self.getDuration(), discount=self.getPercentDiscount()))

    def handleBodyButton(self):
        event_dispatcher.showPremiumWindow()


class BoosterAward(AwardAbstract):

    def __init__(self, booster):
        self._booster = booster

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_BOOSTERAWARD)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return self._booster.bigIcon

    def getHeader(self):
        return text_styles.highTitle(i18n.makeString(MENU.AWARDWINDOW_BOOSTERAWARD_HEADER, boosterName=i18n.makeString(_BOOSTER_DESCRIPTION_LOCALE % self._booster.boosterGuiType, effectValue=self._booster.effectValue)))

    def getDescription(self):
        localKey = '#menu:awardWindow/boosterAward/description/timeValue/%s'
        if self._booster.expiryTime:
            timeValue = text_styles.stats(i18n.makeString(localKey % 'defined', effectTime=self._booster.getEffectTimeStr(), tillTime=self._booster.getExpiryDate()))
        else:
            timeValue = text_styles.stats(i18n.makeString(localKey % 'undefined', effectTime=self._booster.getEffectTimeStr()))
        description = text_styles.main(MENU.AWARDWINDOW_BOOSTERAWARD_DESCRIPTION_TILLTIME)
        return description + timeValue

    def getAdditionalText(self):
        return text_styles.main(MENU.AWARDWINDOW_BOOSTERAWARD_ADDITIONAL)

    def getBodyButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_BOOSTERAWARD_ACTIVATEBTN_LABEL)

    def getButtonStates(self):
        return (False, True, True)

    def handleBodyButton(self):
        event_dispatcher.showBoostersWindow()

    def clear(self):
        self._booster = None
        return


class FalloutAwardWindow(AwardAbstract):
    TITLE_KEY = '#fallout:awardWindow/title/'
    HEADER_KEY = '#fallout:awardWindow/header/'
    MAIN_TEXT_KEY = '#fallout:awardWindow/mainText/'
    ADDITIONAL_TEXT_KEY = '#fallout:awardWindow/additionalText/'
    BTN_ACTION_KEY = '#fallout:awardWindow/btnAction/'
    BTN_CLOSE_KEY = '#fallout:awardWindow/btnClose/'

    def __init__(self, lvls, isRequiredVehicle = False):
        self._lvls = lvls
        self._isMaxLvl = isRequiredVehicle
        if self._isMaxLvl:
            self._typeID = '1'
        else:
            self._typeID = '2'

    def getWindowTitle(self):
        return i18n.makeString(self.TITLE_KEY + self._typeID)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_WINDOWS_FALLOUT_CONGRATULATIONS_BG

    def getHeader(self):
        localeStr = i18n.makeString(self.HEADER_KEY + self._typeID)
        return text_styles.highTitle(localeStr % toRomanRangeString(list(self._lvls), 1))

    def getDescription(self):
        localeStr = i18n.makeString(self.MAIN_TEXT_KEY + self._typeID)
        return text_styles.main(localeStr % toRomanRangeString(list(self._lvls), 1))

    def getAdditionalText(self):
        if not self._isMaxLvl:
            return text_styles.main(self.ADDITIONAL_TEXT_KEY + self._typeID)
        else:
            return super(FalloutAwardWindow, self).getAdditionalText()

    def getHasDashedLine(self):
        if not self._isMaxLvl:
            return True
        else:
            return False

    def getBodyButtonText(self):
        return i18n.makeString(self.BTN_ACTION_KEY + self._typeID)

    def getButtonStates(self):
        return (False, True, True)

    def getTextAreaIconIsShow(self):
        return True

    def getTextAreaIconPath(self):
        return RES_ICONS.MAPS_ICONS_BATTLETYPES_64X64_FALLOUT

    def handleBodyButton(self):
        if self._isMaxLvl:
            from gui.prb_control.context import PrebattleAction
            from gui.prb_control.dispatcher import g_prbLoader
            from gui.prb_control.settings import PREBATTLE_ACTION_NAME
            dispatcher = g_prbLoader.getDispatcher()
            if dispatcher is not None:
                dispatcher.doSelectAction(PrebattleAction(PREBATTLE_ACTION_NAME.FALLOUT))
            else:
                LOG_ERROR('Prebattle dispatcher is not defined')
        else:
            from gui.server_events.events_dispatcher import showEventsWindow
            showEventsWindow(eventType=constants.EVENT_TYPE.BATTLE_QUEST)
        return
