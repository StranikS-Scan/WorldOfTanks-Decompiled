# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/awards/special_achievement_awards.py
import logging
from collections import namedtuple
import BigWorld
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.goodies.goodie_items import _BOOSTER_DESCRIPTION_LOCALE
from gui.server_events.awards import AwardAbstract, ExplosionBackAward
from gui.shared import event_dispatcher as shared_events
from gui.shared.formatters import text_styles
from gui.shared.gui_items.dossier.achievements.abstract import RegularAchievement
from helpers import dependency
from helpers import i18n
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class _AWARD(object):
    MEDAL = 1
    EMBLEM = 2
    INSCRIPTION = 3
    EXP = 4
    STYLE = 5
    BADGE = 6


class _BLOGGER(object):
    USHA = 'Usha'
    JOVE = 'Jove'
    LEBWA = 'LeBwa'
    AMWAY = 'Amway921'


_BLOGGERS = {_BLOGGER.USHA,
 _BLOGGER.JOVE,
 _BLOGGER.LEBWA,
 _BLOGGER.AMWAY}
_BLOGGERS_NAMES = {_BLOGGER.USHA: MENU.AWARDWINDOW_BLOGGERSAWARD_NAME_USHA,
 _BLOGGER.AMWAY: MENU.AWARDWINDOW_BLOGGERSAWARD_NAME_AMWAY,
 _BLOGGER.JOVE: MENU.AWARDWINDOW_BLOGGERSAWARD_NAME_JOVE,
 _BLOGGER.LEBWA: MENU.AWARDWINDOW_BLOGGERSAWARD_NAME_LEBWA}
_BloggerAward = namedtuple('BloggerAward', ('icon', 'text'))
_BLOGGERS_AWARDS = {_AWARD.MEDAL: _BloggerAward(lambda blogger: '%s/%s.png' % (RegularAchievement.ICON_PATH_180X180, ''.join(('streamersEvent', blogger))), lambda blogger: i18n.makeString(MENU.AWARDWINDOW_BLOGGERSAWARD_DESCRIPTION_MEDAL, blogger=i18n.makeString(_BLOGGERS_NAMES[blogger]))),
 _AWARD.EMBLEM: _BloggerAward(RES_ICONS.getBloggerEmblem, lambda blogger: i18n.makeString(MENU.AWARDWINDOW_BLOGGERSAWARD_DESCRIPTION_EMBLEM, blogger=i18n.makeString(_BLOGGERS_NAMES[blogger]))),
 _AWARD.INSCRIPTION: _BloggerAward(RES_ICONS.getBloggerInscription, lambda blogger: i18n.makeString(MENU.AWARDWINDOW_BLOGGERSAWARD_DESCRIPTION_INSCRIPTION, blogger=i18n.makeString(_BLOGGERS_NAMES[blogger]))),
 _AWARD.EXP: _BloggerAward(lambda blogger: RES_ICONS.MAPS_ICONS_BLOGGERS_EXPDOUBLE, lambda blogger: i18n.makeString(MENU.AWARDWINDOW_BLOGGERSAWARD_DESCRIPTION_EXP, blogger=i18n.makeString(_BLOGGERS_NAMES[blogger]))),
 _AWARD.STYLE: _BloggerAward(lambda blogger: RES_ICONS.MAPS_ICONS_BLOGGERS_CUSTOMSTYLE, lambda blogger: i18n.makeString(MENU.AWARDWINDOW_BLOGGERSAWARD_DESCRIPTION_STYLE, blogger=i18n.makeString(_BLOGGERS_NAMES[blogger]))),
 _AWARD.BADGE: _BloggerAward(RES_ICONS.getBloggerBadge, lambda blogger: i18n.makeString(MENU.AWARDWINDOW_BLOGGERSAWARD_DESCRIPTION_BADGE, blogger=i18n.makeString(_BLOGGERS_NAMES[blogger])))}
_logger = logging.getLogger(__name__)

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

    def getOkButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_BOOSTERAWARD_ACTIVATEBTN_LABEL)

    def handleOkButton(self):
        shared_events.showBoostersWindow()

    def clear(self):
        self._booster = None
        return


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
    lobbyContext = dependency.descriptor(ILobbyContext)

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
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_INFO)

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
        if self.__vehicleDesrs:
            serverSettings = self.lobbyContext.getServerSettings()
            vehInvId = self.itemsCache.items.getItemByCD(self.__vehicleDesrs[0]).invID
            provider = BigWorld.player().inventory.getProviderForVehInvId(vehInvId, serverSettings)
            tariff = i18n.makeString(MENU.internetProviderTariff(provider))
        else:
            tariff = ''
        premText = text_styles.neutral(MENU.AWARDWINDOW_TELECOMAWARD_DESCRIPTION_PREM)
        description = i18n.makeString(descriptionKey, tariff=tariff, vehicles=vehicles, prem=premText)
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


class BloggersBattleAward(ExplosionBackAward):

    def __init__(self, awardId, blogger):
        super(BloggersBattleAward, self).__init__()
        self._awardId = _AWARD.MEDAL
        self._blogger = _BLOGGER.USHA
        if self.__checkAward(awardId):
            self._awardId = awardId
        if self.__checkBlogger(blogger):
            self._blogger = blogger

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_BLOGGERSAWARD)

    def getAwardImage(self):
        return _BLOGGERS_AWARDS[self._awardId].icon(self._blogger)

    def getHeader(self):
        return text_styles.alignText(text_styles.superPromoTitle(MENU.AWARDWINDOW_BLOGGERSAWARD_HEADER), 'center')

    def getDescription(self):
        return text_styles.alignText(text_styles.main(i18n.makeString(MENU.AWARDWINDOW_BLOGGERSAWARD_DESCRIPTION, awardName=i18n.makeString(_BLOGGERS_AWARDS[self._awardId].text(self._blogger)))), 'center')

    def clear(self):
        self._awardId = None
        return

    def __checkAward(self, awardId):
        if _AWARD.MEDAL <= awardId <= _AWARD.BADGE:
            return True
        _logger.warning('Bloggers award ID = %d is out of range %d-%d', awardId, _AWARD.MEDAL, _AWARD.BADGE)
        return False

    def __checkBlogger(self, blogger):
        if blogger in _BLOGGERS:
            return True
        _logger.warning('Incorrect blogger name %s. Should be one of %s', blogger, str(_BLOGGERS))
        return False
