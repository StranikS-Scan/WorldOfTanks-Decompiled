# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/awards/special_achievement_awards.py
import BigWorld
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.lobby.PersonalCaseConstants import TABS
from gui.referral_program import REFERRAL_PROGRAM_SOUNDS
from gui.server_events.awards import AwardAbstract, ExplosionBackAward
from gui.shared import event_dispatcher as shared_events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showReferralProgramWindow
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import sortCrew
from gui.impl.gen import R
from gui.impl import backport
from helpers import dependency
from helpers import i18n
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from CurrentVehicle import g_currentVehicle

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


class CrewSkinAward(ExplosionBackAward):

    def __init__(self):
        super(CrewSkinAward, self).__init__(False)

    def getWindowTitle(self):
        return backport.text(R.strings.crew_skins.feature.poster.posterHeader())

    def getBackgroundImage(self):
        return backport.image(R.images.gui.maps.icons.windows.rewardWindow.crewSkins_presentation())

    def getHeader(self):
        return text_styles.highTitle(backport.text(R.strings.crew_skins.feature.poster.giftName()))

    def getOkButtonText(self):
        return backport.text(R.strings.crew_skins.feature.poster.confirm()) if self._getFirstEnableTankman() is not None else backport.text(R.strings.menu.awardWindow.okButton())

    def getDescription(self):
        return text_styles.main(backport.text(R.strings.crew_skins.feature.poster.featureDescr()))

    @staticmethod
    def _getFirstEnableTankman():
        vehicleGuiItem = g_currentVehicle.item
        if vehicleGuiItem is not None and not vehicleGuiItem.isLocked:
            roles = g_currentVehicle.item.descriptor.type.crewRoles
            crew = sortCrew(vehicleGuiItem.crew, roles)
            for _, tankman in crew:
                if tankman is not None and not tankman.descriptor.getRestrictions().isPassportReplacementForbidden():
                    return tankman

        return

    def handleOkButton(self):
        tankman = self._getFirstEnableTankman()
        if tankman is not None:
            shared_events.showPersonalCase(tankman.invID, TABS.CREW_SKINS_TAB_INDEX, EVENT_BUS_SCOPE.LOBBY)
        return


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
        return text_styles.highTitle(i18n.makeString(MENU.AWARDWINDOW_BOOSTERAWARD_HEADER, boosterName=i18n.makeString(MENU.boosterDescriptionLocale(self._booster.boosterGuiType), effectValue=self._booster.getFormattedValue(text_styles.highTitle))))

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
        item = self.itemsCache.items.getItemByCD(self.__vehicleDesrs[0])
        if hasattr(item, 'invID'):
            g_currentVehicle.selectVehicle(item.invID)
        shared_events.showHangar()


class RecruiterAward(ExplosionBackAward):

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_RECRUITERAWARD_TITLE)

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_AWARDS_BECOMERECRUITER

    def getHeader(self):
        return text_styles.promoTitle(text_styles.alignText(i18n.makeString(MENU.AWARDWINDOW_RECRUITERAWARD_HEADER), 'center'))

    def getOkButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_RECRUITERAWARD_OKBUTTON)

    def getDescription(self):
        return text_styles.main(text_styles.alignText(i18n.makeString(MENU.AWARDWINDOW_RECRUITERAWARD_DESCRIPTION), 'center'))

    def handleOkButton(self):
        showReferralProgramWindow()

    def getSound(self):
        return REFERRAL_PROGRAM_SOUNDS.RECRUITER_AWARD
