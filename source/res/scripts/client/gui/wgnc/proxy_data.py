# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgnc/proxy_data.py
from account_helpers import getAccountDatabaseID
from adisp import process
from gui.Scaleform.daapi.view.lobby.referral_program.referral_program_helpers import getReferralProgramURL
from gui.Scaleform.locale.MENU import MENU
from gui.awards.event_dispatcher import showRecruiterAward
from gui.marathon.racing_event import TOURNAMENT_END_FAKE_TOKEN, TOURNAMENT_STAGE_END_FAKE_TOKEN, RacingEvent
from gui.promo.promo_logger import PromoLogSourceType, PromoLogActions
from gui.shared.event_dispatcher import showReferralProgramWindow
from gui.wgnc.common import WebHandlersContainer
from gui.wgnc.events import g_wgncEvents
from gui.wgnc.settings import WGNC_DATA_PROXY_TYPE
from helpers import dependency
from skeletons.gui.game_control import IEncyclopediaController, IBrowserController, IPromoController, IReferralProgramController, IMarathonEventsController
from skeletons.gui.shared.promo import IPromoLogger

class _ProxyDataItem(object):

    def getType(self):
        raise NotImplementedError

    def show(self, notID):
        g_wgncEvents.onProxyDataItemShowByDefault(notID, self)


class _ClanBaseAooItem(_ProxyDataItem):

    def getID(self):
        pass


class ClanApplicationItem(_ClanBaseAooItem):

    def __init__(self, account_id, application_id, active_applications_count):
        super(ClanApplicationItem, self).__init__()
        self.__accountId = account_id
        self.__appId = application_id
        self.__applicationsCount = active_applications_count

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_APP

    def getAccountID(self):
        return self.__accountId

    def getApplicationID(self):
        return self.__appId

    def getActiveApplicationsCount(self):
        return self.__applicationsCount

    def getID(self):
        return self.getApplicationID()


class _ClanApplicationActionItem(_ProxyDataItem):

    def __init__(self, account_id, application_id):
        super(_ClanApplicationActionItem, self).__init__()
        self.__accountId = account_id
        self.__appId = application_id

    def getAccountID(self):
        return self.__accountId

    def getApplicationID(self):
        return self.__appId


class ClanAppAcceptedActionItem(_ClanApplicationActionItem):

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_APP_ACCEPTED_FOR_MEMBERS


class ClanAppDeclinedActionItem(_ClanApplicationActionItem):

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_APP_DECLINED_FOR_MEMBERS


class ClanInviteItem(_ClanBaseAooItem):

    def __init__(self, invite_id, clan_id, clan_name, clan_tag, active_invites_count):
        super(ClanInviteItem, self).__init__()
        self.__inviteId = invite_id
        self.__clanId = clan_id
        self.__clanName = clan_name
        self.__clanTag = clan_tag
        self.__activeInvitesCount = active_invites_count

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_INVITE

    def getInviteId(self):
        return self.__inviteId

    def getClanId(self):
        return self.__clanId

    def getClanName(self):
        return self.__clanName

    def getClanTag(self):
        return self.__clanTag

    def getActiveInvitesCount(self):
        return self.__activeInvitesCount

    def getID(self):
        return self.getInviteId()

    def getAccountDbID(self):
        return getAccountDatabaseID()


class _ClanPersonalAppItem(_ProxyDataItem):

    def __init__(self, clan_id, clan_name, clan_tag, application_id):
        super(_ClanPersonalAppItem, self).__init__()
        self.__clanId = clan_id
        self.__clanName = clan_name
        self.__clanTag = clan_tag
        self.__applicationId = application_id

    def getClanId(self):
        return self.__clanId

    def getClanName(self):
        return self.__clanName

    def getClanTag(self):
        return self.__clanTag

    def getApplicationId(self):
        return self.__applicationId


class ClanAppDeclinedItem(_ClanPersonalAppItem):

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_APP_DECLINED


class ClanAppAcceptedItem(_ClanPersonalAppItem):

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_APP_ACCEPTED


class _ClanInviteActionResultItem(_ProxyDataItem):

    def __init__(self, account_id, invite_id):
        super(_ClanInviteActionResultItem, self).__init__()
        self.__accountId = account_id
        self.__inviteId = invite_id

    def getAccountID(self):
        return self.__accountId

    def getInviteId(self):
        return self.__inviteId

    def getID(self):
        return self.getInviteId()


class ClanInviteDeclinedItem(_ClanInviteActionResultItem):

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_INVITE_DECLINED


class ClanInvitesCreatedItem(_ProxyDataItem):

    def __init__(self, account_id, invite_id):
        super(ClanInvitesCreatedItem, self).__init__()
        self.__accountIds = account_id
        self.__inviteIds = invite_id

    def getAccountIDs(self):
        return self.__accountIds

    def getInviteIds(self):
        return self.__inviteIds

    def getNewInvitesCount(self):
        return len(self.__inviteIds)

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_INVITES_CREATED


class ClanInviteAcceptedItem(_ClanInviteActionResultItem):

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.CLAN_INVITE_ACCEPTED


class EncyclopediaContentItem(_ProxyDataItem):
    encyclopedia = dependency.descriptor(IEncyclopediaController)

    def __init__(self, contentId):
        self.__contentId = contentId

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.ENCYCLOPEDIA_CONTENT_RECEIVED

    def show(self, _):
        self.encyclopedia.addEncyclopediaRecommendation(self.__contentId)


class ShowTeaserItem(_ProxyDataItem):
    _promoCtrl = dependency.descriptor(IPromoController)

    def __init__(self, data):
        self.__data = data

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.SHOW_PROMO_TEASER

    def show(self, _):
        dependency.instance(IPromoLogger).logTeaserAction(self.__data['lastPromo'], action=PromoLogActions.RECEIVED_WGNC, source=PromoLogSourceType.WGNC)
        self._promoCtrl.setNewTeaserData(self.__data)


class ShowInBrowserItem(_ProxyDataItem, WebHandlersContainer):
    browserCtrl = dependency.descriptor(IBrowserController)

    def __init__(self, url, size=None, title=None, showRefresh=False, webHandlerName='', titleKey='', isSolidBorder=False):
        self.__url = url
        self.__size = size
        self.__title = title
        self.__titleKey = titleKey
        self.__showRefresh = showRefresh
        self.__webHandlerName = webHandlerName
        self.__isSolidBorder = isSolidBorder

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.SHOW_IN_BROWSER

    @process
    def show(self, _):
        browserId = yield self.browserCtrl.load(self.__url, browserSize=self.__size, title=self.__getTitle(), showActionBtn=self.__showRefresh, handlers=self.getWebHandler(self.__webHandlerName), isSolidBorder=self.__isSolidBorder)
        browser = self.browserCtrl.getBrowser(browserId)
        if browser:
            browser.useSpecialKeys = False

    def __getTitle(self):
        localizedValue = None
        if self.__titleKey:
            localizedValue = MENU.browser_customtitle(self.__titleKey)
        return localizedValue or self.__title


class UpdateRefferalBubbleItem(_ProxyDataItem):
    _referralCtrl = dependency.descriptor(IReferralProgramController)

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.UPDATE_REFERRAL_BUBBLE

    def show(self, _):
        self._referralCtrl.updateBubble()


class BecomeRecruiterItem(_ProxyDataItem):

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.BECOME_RECRUITER

    def show(self, _):
        showRecruiterAward()


class ShowReferralWindowItem(_ProxyDataItem):

    def __init__(self, relativeUrl=None):
        self.__relativeUrl = relativeUrl if relativeUrl is not None else ''
        return

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.SHOW_REFERRAL_WINDOW

    def show(self, _):
        url = getReferralProgramURL() + self.__relativeUrl
        showReferralProgramWindow(url)


class RacingTournamentEndItem(_ProxyDataItem):
    _marathonEventsController = dependency.descriptor(IMarathonEventsController)

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.RACING_TOURNAMENT_END

    def show(self, _):
        marathonEvent = self._marathonEventsController.getMarathon(RacingEvent.RACING_MARATHON_PREFIX)
        if marathonEvent is not None:
            self._setAwardReceived(marathonEvent)
            self._marathonEventsController.tryShowRewardScreen()
        return

    def _setAwardReceived(self, marathonEvent):
        marathonEvent.addAwardToQueue(TOURNAMENT_END_FAKE_TOKEN)


class RacingTournamentStageEndItem(RacingTournamentEndItem):

    def __init__(self, stageNumber):
        super(RacingTournamentStageEndItem, self).__init__()
        self.__stageNumber = stageNumber

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.RACING_TOURNAMENT_STAGE_END

    def _setAwardReceived(self, marathonEvent):
        marathonEvent.addAwardToQueue(TOURNAMENT_STAGE_END_FAKE_TOKEN + str(self.__stageNumber))


class ProxyDataHolder(object):

    def __init__(self, items):
        super(ProxyDataHolder, self).__init__()
        self.__items = {item.getType():item for item in items}

    def all(self):
        return self.__items.itervalues()

    def hasItemType(self, itemType):
        return itemType in self.__items

    def getItemByType(self, itemType):
        item = None
        if self.hasItemType(itemType):
            item = self.__items[itemType]
        return item
