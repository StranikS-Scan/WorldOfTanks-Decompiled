# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/awards/special_achievement_awards.py
import BigWorld
import constants
from adisp import process
from debug_utils import LOG_ERROR
from gui.Scaleform.locale.CLANS import CLANS
from gui.goodies.goodie_items import _BOOSTER_DESCRIPTION_LOCALE
from gui.shared import event_dispatcher as shared_events
from gui.shared.formatters import text_styles
from gui.shared.formatters.ranges import toRomanRangeString
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.lobby.AwardWindow import AwardAbstract, ExplosionBackAward
from helpers import dependency
from helpers import i18n
from skeletons.gui.shared import IItemsCache

class ResearchAward(ExplosionBackAward):

    def __init__(self, vehiclesCount, messageNumber):
        super(ResearchAward, self).__init__()
        self.vehiclesCount = vehiclesCount
        self.messageNumber = messageNumber

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_SPECIALACHIEVEMENT)

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_AWARDS_VEHICLESRESEARCH

    def getHeader(self):
        return text_styles.highTitle(i18n.makeString(MENU.AWARDWINDOW_SPECIALACHIEVEMENT_HEADER))

    def getDescription(self):
        return text_styles.main(i18n.makeString('#menu:awardWindow/specialAchievement/research/description%d' % self.messageNumber, vehiclesCount=self.vehiclesCount))


class VictoryAward(ExplosionBackAward):

    def __init__(self, victoriesCount, messageNumber):
        super(VictoryAward, self).__init__()
        self.victoriesCount = victoriesCount
        self.messageNumber = messageNumber

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_SPECIALACHIEVEMENT)

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_AWARDS_VICTORY

    def getHeader(self):
        return text_styles.highTitle(i18n.makeString(MENU.AWARDWINDOW_SPECIALACHIEVEMENT_HEADER))

    def getDescription(self):
        return text_styles.main(i18n.makeString('#menu:awardWindow/specialAchievement/victory/description%d' % self.messageNumber, victoriesCount=BigWorld.wg_getIntegralFormat(self.victoriesCount)))


class BattleAward(ExplosionBackAward):

    def __init__(self, battlesCount, messageNumber):
        super(BattleAward, self).__init__()
        self.battlesCount = battlesCount
        self.messageNumber = messageNumber

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_SPECIALACHIEVEMENT)

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_AWARDS_BATTLESWORDS

    def getHeader(self):
        return text_styles.highTitle(i18n.makeString(MENU.AWARDWINDOW_SPECIALACHIEVEMENT_HEADER))

    def getDescription(self):
        return text_styles.main(i18n.makeString('#menu:awardWindow/specialAchievement/battle/description%d' % self.messageNumber, battlesCount=BigWorld.wg_getIntegralFormat(self.battlesCount)))


class PvEBattleAward(BattleAward):

    def getWindowTitle(self):
        return i18n.makeString('#menu:awardWindow/title/info')

    def getDescription(self):
        return text_styles.main(i18n.makeString('#menu:awardWindow/specialAchievement/pveBattle/description', battlesCount=self.battlesCount))

    def handleOkButton(self):
        shared_events.runTutorialChain('PvE_Chain')

    def handleCloseButton(self):
        shared_events.runTutorialChain('PvE_Chain')


class BoosterAward(ExplosionBackAward):

    def __init__(self, booster):
        super(BoosterAward, self).__init__()
        self._booster = booster

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_BOOSTERAWARD)

    def getAwardImage(self):
        return self._booster.bigIcon

    def getHeader(self):
        return text_styles.highTitle(i18n.makeString(MENU.AWARDWINDOW_BOOSTERAWARD_HEADER, boosterName=i18n.makeString(_BOOSTER_DESCRIPTION_LOCALE % self._booster.boosterGuiType, effectValue=self._booster.getFormattedValue(text_styles.highTitle))))

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
        shared_events.showBoostersWindow()

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

    def __init__(self, lvls, isRequiredVehicle=False):
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
        return not self._isMaxLvl

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
            from gui.prb_control.entities.base.ctx import PrbAction
            from gui.prb_control.dispatcher import g_prbLoader
            from gui.prb_control.settings import PREBATTLE_ACTION_NAME
            dispatcher = g_prbLoader.getDispatcher()
            if dispatcher is not None:
                self.__doSelect(dispatcher)
            else:
                LOG_ERROR('Prebattle dispatcher is not defined')
        else:
            from gui.server_events.events_dispatcher import showEventsWindow
            showEventsWindow(eventType=constants.EVENT_TYPE.BATTLE_QUEST)
        return

    @process
    def __doSelect(self, dispatcher):
        from gui.prb_control.entities.base.ctx import PrbAction
        from gui.prb_control.settings import PREBATTLE_ACTION_NAME
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.FALLOUT))


class ClanJoinAward(AwardAbstract):

    def __init__(self, clanAbbrev, clanName, clanDbID):
        super(ClanJoinAward, self).__init__()
        self.clanAbbrev = clanAbbrev
        self.clanName = clanName
        self.clanDbID = clanDbID
        self.rank = i18n.makeString(CLANS.CLAN_POST_RECRUIT)

    def getWindowTitle(self):
        return i18n.makeString(CLANS.CLANPROFILE_CLANJOINAWARD_TITLE)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_CLANS_PIC_CLAN_IVITATION_BACK

    def getHeader(self):
        return text_styles.highTitle(i18n.makeString(CLANS.CLANPROFILE_CLANJOINAWARD_HEADER))

    def getDescription(self):
        return text_styles.main(i18n.makeString(CLANS.CLANPROFILE_CLANJOINAWARD_YOURCLAN, tag=text_styles.stats(self.clanAbbrev), clanName=text_styles.stats(self.clanName)))

    def getAdditionalText(self):
        return text_styles.main(i18n.makeString(CLANS.CLANPROFILE_CLANJOINAWARD_SECONDARYTEXT))

    def getBodyButtonText(self):
        return i18n.makeString(CLANS.CLANPROFILE_CLANJOINAWARD_BTNACTION)

    def getButtonStates(self):
        return (False, True, True)

    def handleBodyButton(self):
        shared_events.showClanProfileWindow(self.clanDbID, self.clanAbbrev)

    def clear(self):
        pass


class TelecomAward(AwardAbstract):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicleDesrs, hasCrew, hasBrotherhood):
        super(TelecomAward, self).__init__()
        self.__vehicleDesrs = vehicleDesrs
        self.__hasCrew = hasCrew
        self.__hasBrotherhood = hasBrotherhood

    def __getVehicleDetails(self, vehicleCD):
        details = {}
        item = self.itemsCache.items.getItemByCD(vehicleCD)
        details['type'] = item.typeUserName
        details['nation'] = i18n.makeString(MENU.nations(item.nationName))
        details['vehicle'] = item.userName
        return details

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_SPECIALACHIEVEMENT)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_AWARDS_USSR_R127_T44_100_P

    def getHeader(self):
        return text_styles.highTitle(MENU.AWARDWINDOW_TELECOMAWARD_HEADER)

    def getDescription(self):
        vehicleNames = []
        for vehCD in self.__vehicleDesrs:
            details = self.__getVehicleDetails(vehCD)
            vehicleNames.append(i18n.makeString(MENU.AWARDWINDOW_TELECOMAWARD_VEHICLES, **details))

        vehicles = '\n'.join(vehicleNames)
        if self.__hasCrew:
            if self.__hasBrotherhood:
                descriptionKey = MENU.AWARDWINDOW_TELECOMAWARD_DESCRIPTION_WITHBROTHERHOOD
            else:
                descriptionKey = MENU.AWARDWINDOW_TELECOMAWARD_DESCRIPTION
        else:
            descriptionKey = MENU.AWARDWINDOW_TELECOMAWARD_DESCRIPTION_WITHOUTCREW
        premText = text_styles.neutral(MENU.AWARDWINDOW_TELECOMAWARD_DESCRIPTION_PREM)
        description = i18n.makeString(descriptionKey, vehicles=vehicles, prem=premText)
        return text_styles.main(description)

    def getAdditionalText(self):
        return text_styles.standard(MENU.AWARDWINDOW_TELECOMAWARD_SUBDESCRIPTION)

    def getButtonStates(self):
        return (False, True, True)

    def getBodyButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_TELECOMAWARD_BUTTON_LABEL)

    def handleBodyButton(self):
        from CurrentVehicle import g_currentVehicle
        item = self.itemsCache.items.getItemByCD(self.__vehicleDesrs[0])
        if hasattr(item, 'invID'):
            g_currentVehicle.selectVehicle(item.invID)
        shared_events.showHangar()
