# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/awards/special_achievement_awards.py
from collector_vehicle import CollectorVehicleConsts
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.referral_program import REFERRAL_PROGRAM_SOUNDS
from gui.server_events.awards import AwardAbstract, ExplosionBackAward
from gui.shared import event_dispatcher as shared_events
from gui.shared.event_dispatcher import showReferralProgramWindow
from gui.shared.formatters import text_styles
from gui.impl.gen import R
from gui.impl import backport
from helpers import dependency, i18n, int2roman
from nations import NAMES
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from CurrentVehicle import g_currentVehicle
_CENTER_ALIGN = 'center'

def _getNationName(nationID):
    return backport.text(R.strings.nations.dyn(NAMES[nationID]).genetiveCase())


class VehicleCollectorAward(ExplosionBackAward):

    def __init__(self, nationID):
        super(VehicleCollectorAward, self).__init__()
        self.__nationID = nationID

    def getBackgroundImage(self):
        return backport.image(R.images.gui.maps.icons.vehicleCollector.collectorNation())

    def useBackgroundAnimation(self):
        return False

    def getAwardImage(self):
        medalName = ''.join((CollectorVehicleConsts.COLLECTOR_MEDAL_PREFIX, str(self.__nationID)))
        return backport.image(R.images.gui.maps.icons.achievement.big.dyn(medalName)())

    def getWindowTitle(self):
        return backport.text(R.strings.menu.awardWindow.vehicleCollector.title(), nation=_getNationName(self.__nationID))

    def getHeader(self):
        return text_styles.promoTitle(text_styles.alignText(backport.text(R.strings.menu.awardWindow.vehicleCollector.header()), _CENTER_ALIGN))

    def getDescription(self):
        return text_styles.alignText(text_styles.main(backport.text(R.strings.menu.awardWindow.vehicleCollector.description(), nation=_getNationName(self.__nationID))), _CENTER_ALIGN)

    def getOkButtonText(self):
        return backport.text(R.strings.menu.awardWindow.vehicleCollector.okButton())


class VehicleCollectorOfEverythingAward(ExplosionBackAward):

    def useBackgroundAnimation(self):
        return False

    def getBackgroundImage(self):
        return backport.image(R.images.gui.maps.icons.vehicleCollector.collectorEverything())

    def getAwardImage(self):
        return backport.image(R.images.gui.maps.icons.achievement.big.collectorVehicle())

    def getWindowTitle(self):
        return backport.text(R.strings.menu.awardWindow.vehicleCollectorOfEverything.title())

    def getHeader(self):
        return text_styles.promoTitle(text_styles.alignText(backport.text(R.strings.menu.awardWindow.vehicleCollectorOfEverything.header()), _CENTER_ALIGN))

    def getDescription(self):
        return text_styles.alignText(text_styles.main(backport.text(R.strings.menu.awardWindow.vehicleCollectorOfEverything.description())), _CENTER_ALIGN)

    def getOkButtonText(self):
        return backport.text(R.strings.menu.awardWindow.vehicleCollectorOfEverything.okButton())


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
        if self._booster.useby:
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
        shared_events.showStorage(STORAGE_CONSTANTS.PERSONAL_RESERVES)

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

    def __init__(self, vehicleDesrs, telecomBundleId, hasCrew, hasBrotherhood):
        super(TelecomAward, self).__init__()
        self.__vehicleDesrs = vehicleDesrs
        self.__provider = self.__getProvider(telecomBundleId)
        self.__hasCrew = hasCrew
        self.__hasBrotherhood = hasBrotherhood

    def __getProvider(self, telecomBundleId):
        telecomConfig = self.lobbyContext.getServerSettings().telecomConfig
        return telecomConfig.getInternetProvider(telecomBundleId)

    def __getVehicleDetails(self, vehicleCD):
        details = {}
        item = self.itemsCache.items.getItemByCD(vehicleCD)
        details['type'] = item.typeUserName
        details['nation'] = backport.text(R.strings.menu.nations.dyn(item.nationName)())
        details['level'] = int2roman(item.level)
        details['vehicle'] = item.userName
        return details

    def getWindowTitle(self):
        return backport.text(self.__addProviderToRes(R.strings.menu.awardWindow.telecomAward.title)())

    def getBackgroundImage(self):
        return backport.image(self.__addProviderToRes(R.images.gui.maps.icons.awards.telecom.bg)())

    def getAwardImage(self):
        return backport.image(self.__addProviderToRes(R.images.gui.maps.icons.awards.telecom.vehicle)())

    def getHeader(self):
        return text_styles.highTitle(backport.text(self.__addProviderToRes(R.strings.menu.awardWindow.telecomAward.header)()))

    def getDescription(self):
        vehicleNames = []
        for vehCD in self.__vehicleDesrs:
            details = self.__getVehicleDetails(vehCD)
            vehicleNames.append(backport.text(self.__addProviderToRes(R.strings.menu.awardWindow.telecomAward.vehicles)(), **details))

        vehicles = '\n'.join(vehicleNames)
        if self.__hasCrew:
            if self.__hasBrotherhood:
                descriptionRes = R.strings.menu.awardWindow.telecomAward.description.withBrotherhood
            else:
                descriptionRes = R.strings.menu.awardWindow.telecomAward.description.full
        else:
            descriptionRes = R.strings.menu.awardWindow.telecomAward.description.withoutCrew
        providerLocRes = R.strings.menu.internet_provider.dyn(self.__provider)
        premText = text_styles.neutral(backport.text(self.__addProviderToRes(R.strings.menu.awardWindow.telecomAward.description.prem)()))
        description = backport.text(self.__addProviderToRes(descriptionRes)(), tariff=backport.text(providerLocRes.tariff()) if providerLocRes else '', vehicles=vehicles, prem=premText)
        return text_styles.main(description)

    def getAdditionalText(self):
        return text_styles.standard(backport.text(self.__addProviderToRes(R.strings.menu.awardWindow.telecomAward.subdescription)()))

    def getButtonStates(self):
        return (False, True, True)

    def getBodyButtonText(self):
        return backport.text(self.__addProviderToRes(R.strings.menu.awardWindow.telecomAward.button.label)())

    def handleBodyButton(self):
        item = self.itemsCache.items.getItemByCD(self.__vehicleDesrs[0])
        if hasattr(item, 'invID'):
            g_currentVehicle.selectVehicle(item.invID)
        shared_events.showHangar()

    def __addProviderToRes(self, res):
        return res.dyn(self.__provider, res.default)


class RecruiterAward(ExplosionBackAward):

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_RECRUITERAWARD_TITLE)

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_AWARDS_BECOMERECRUITER

    def getHeader(self):
        return text_styles.promoTitle(text_styles.alignText(i18n.makeString(MENU.AWARDWINDOW_RECRUITERAWARD_HEADER), _CENTER_ALIGN))

    def getOkButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_RECRUITERAWARD_OKBUTTON)

    def getDescription(self):
        return text_styles.main(text_styles.alignText(i18n.makeString(MENU.AWARDWINDOW_RECRUITERAWARD_DESCRIPTION), _CENTER_ALIGN))

    def handleOkButton(self):
        showReferralProgramWindow()

    def getSound(self):
        return REFERRAL_PROGRAM_SOUNDS.RECRUITER_AWARD
