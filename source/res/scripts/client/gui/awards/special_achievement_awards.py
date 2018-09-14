# Embedded file name: scripts/client/gui/awards/special_achievement_awards.py
import BigWorld
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES
from gui.goodies.Booster import _BOOSTER_DESCRIPTION_LOCALE
from gui.shared import event_dispatcher
from gui.shared.formatters import text_styles
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
        return self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.HIGH_TITLE, i18n.makeString(MENU.AWARDWINDOW_SPECIALACHIEVEMENT_HEADER))

    def getDescription(self):
        return self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.MAIN_TEXT, i18n.makeString('#menu:awardWindow/specialAchievement/research/description%d' % self.messageNumber, vehiclesCount=self.vehiclesCount))


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
        return self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.HIGH_TITLE, i18n.makeString(MENU.AWARDWINDOW_SPECIALACHIEVEMENT_HEADER))

    def getDescription(self):
        return self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.MAIN_TEXT, i18n.makeString('#menu:awardWindow/specialAchievement/victory/description%d' % self.messageNumber, victoriesCount=self.victoriesCount))


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
        return self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.HIGH_TITLE, i18n.makeString(MENU.AWARDWINDOW_SPECIALACHIEVEMENT_HEADER))

    def getDescription(self):
        return self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.MAIN_TEXT, i18n.makeString('#menu:awardWindow/specialAchievement/battle/description%d' % self.messageNumber, battlesCount=self.battlesCount))


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
        return i18n.makeString(MENU.PREMIUM_CANCEL)

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
        timeValue = text_styles.stats(i18n.makeString(MENU.AWARDWINDOW_BOOSTERAWARD_DESCRIPTION_TIMEVALUE, effectTime=self._booster.getEffectTimeStr(), tillTime=self._booster.getExpiryDate()))
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
