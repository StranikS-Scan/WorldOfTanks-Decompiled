# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgnc/proxy_data.py
from account_helpers import getAccountDatabaseID
from adisp import adisp_process
from gui.Scaleform.daapi.view.lobby.referral_program.referral_program_helpers import getReferralProgramURL
from gui.Scaleform.locale.MENU import MENU
from gui.awards.event_dispatcher import showRecruiterAward
from gui.integrated_auction.messages import pushRateErrorMessage, pushBelowCompetitiveRateMessage
from gui.promo.promo_logger import PromoLogSourceType, PromoLogActions
from gui.shared.event_dispatcher import showReferralProgramWindow
from gui.wgnc.common import WebHandlersContainer
from gui.wgnc.events import g_wgncEvents
from gui.wgnc.settings import WGNC_DATA_PROXY_TYPE
from helpers import dependency
from gui.wgnc.image_notification_helper import showPaymentMethodLinkNotification, showPaymentMethodUnlinkNotification
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.game_control import IBrowserController, IPromoController, IReferralProgramController, IClanNotificationController
from skeletons.gui.shared.promo import IPromoLogger
from skeletons.gui.system_messages import ISystemMessages

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

    @adisp_process
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


class UpdateClanNotificationItem(_ProxyDataItem):
    _notificationCtrl = dependency.descriptor(IClanNotificationController)

    def __init__(self, alias, value, isIncrement):
        self._alias = alias
        self._value = value
        self._isIncrement = isIncrement

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.UPDATE_CLAN_NOTIFICATION

    def show(self, notID):
        self._notificationCtrl.setCounters(self._alias, self._value, self._isIncrement)


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


class PaymentMethodChangeItem(_ProxyDataItem):

    def __init__(self, operation, method, cdnUrl):
        self.__operation = operation
        self.__method = method
        self.__cdnUrl = cdnUrl

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.PAYMENT_METHOD_CHANGE_NOTIFICATION

    def show(self, _):
        if self.__operation == 'link':
            showPaymentMethodLinkNotification(self.__method, self.__cdnUrl)
        elif self.__operation == 'unlink':
            showPaymentMethodUnlinkNotification(self.__method, self.__cdnUrl)


class ShowMapboxSurveyAvailableMessage(_ProxyDataItem):
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self, mapName):
        self.__mapName = mapName

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.MAPBOX_SURVEY_AVAILABLE_NOTIFICATION

    def show(self, _):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({'map': self.__mapName,
         'msgType': SCH_CLIENT_MSG_TYPE.MAPBOX_SURVEY_AVAILABLE}, SCH_CLIENT_MSG_TYPE.MAPBOX_SURVEY_AVAILABLE)


class ShowMapboxEventStartedMessage(_ProxyDataItem):
    __systemMessages = dependency.descriptor(ISystemMessages)

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.MAPBOX_EVENT_STARTED_NOTIFICATION

    def show(self, _):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({}, SCH_CLIENT_MSG_TYPE.MAPBOX_EVENT_STARTED)


class ShowMapboxEventEndedMessage(_ProxyDataItem):
    __systemMessages = dependency.descriptor(ISystemMessages)

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.MAPBOX_EVENT_ENDED_NOTIFICATION

    def show(self, _):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({}, SCH_CLIENT_MSG_TYPE.MAPBOX_EVENT_ENDED)


class ShowMapboxRewardReceivedMessage(_ProxyDataItem):
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self, rewardData):
        self.__rewardData = rewardData

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.MAPBOX_REWARD_RECEIVED_NOTIFICATION

    def show(self, _):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({'rewards': self.__rewardData['rewards'],
         'battles': self.__rewardData['battles'],
         'isFinal': self.__rewardData['isFinal'],
         'msgType': SCH_CLIENT_MSG_TYPE.MAPBOX_PROGRESSION_REWARD}, SCH_CLIENT_MSG_TYPE.MAPBOX_PROGRESSION_REWARD)


class ShowAuctionRateErrorMessage(_ProxyDataItem):
    __systemMessages = dependency.descriptor(ISystemMessages)

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.INTEGRATED_AUCTION_RATE_ERROR

    def show(self, _):
        pushRateErrorMessage(systemMessages=self.__systemMessages)


class ShowAuctionBelowCompetitiveRateMessage(_ProxyDataItem):
    __systemMessages = dependency.descriptor(ISystemMessages)

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.INTEGRATED_AUCTION_RATE_BELOW_COMPETITIVE

    def show(self, _):
        pushBelowCompetitiveRateMessage(systemMessages=self.__systemMessages)


class ShowAuctionLostRateMessage(_ProxyDataItem):
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self, messageData):
        self.__messageData = messageData

    def getType(self):
        return WGNC_DATA_PROXY_TYPE.INTEGRATED_AUCTION_RATE_LOST

    def show(self, _):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({'data': self.__messageData,
         'msgType': SCH_CLIENT_MSG_TYPE.INTEGRATED_AUCTION_LOST_RATE}, SCH_CLIENT_MSG_TYPE.INTEGRATED_AUCTION_LOST_RATE)


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
