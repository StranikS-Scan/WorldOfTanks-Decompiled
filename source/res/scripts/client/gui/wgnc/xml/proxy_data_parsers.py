# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgnc/xml/proxy_data_parsers.py
import logging
import json
from gui.wgcg.promo_screens.parsers import PromoDataParser
from gui.wgnc import proxy_data
from gui.wgnc.wgnc_helpers import parseSize
from gui.wgnc.xml.shared_parsers import ParsersCollection, SectionParser
_logger = logging.getLogger(__name__)

class _ClanApplicationParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        return proxy_data.ClanApplicationItem(section.readInt64('account_id'), section.readInt64('application_id'), section.readInt('active_applications_count'))


class _ClanAppActionParser(SectionParser):

    def parse(self, section):
        return self._getItemClass()(section.readInt64('account_id'), section.readInt64('application_id'))

    def _getItemClass(self):
        raise NotImplementedError


class _ClanAppAcceptedActionParser(_ClanAppActionParser):

    def getTagName(self):
        pass

    def _getItemClass(self):
        return proxy_data.ClanAppAcceptedActionItem


class _ClanAppDeclinedActionParser(_ClanAppActionParser):

    def getTagName(self):
        pass

    def _getItemClass(self):
        return proxy_data.ClanAppDeclinedActionItem


class _ClanInviteParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        return proxy_data.ClanInviteItem(section.readInt('invite_id'), section.readInt64('clan_id'), self._readString('clan_name', section), self._readString('clan_tag', section), section.readInt('active_invites_count'))


class _ClanPersonalAppParser(SectionParser):

    def parse(self, section):
        return self._createItem(section.readInt64('clan_id'), self._readString('clan_name', section), self._readString('clan_tag', section), section.readInt64('application_id'))

    def _createItem(self, cId, cName, cTag, appId):
        raise NotImplementedError


class _ClanAppAcceptedParser(_ClanPersonalAppParser):

    def getTagName(self):
        pass

    def _createItem(self, cId, cName, cTag, appId):
        return proxy_data.ClanAppAcceptedItem(cId, cName, cTag, appId)


class _ClanAppDeclinedParser(_ClanPersonalAppParser):

    def getTagName(self):
        pass

    def _createItem(self, cId, cName, cTag, appId):
        return proxy_data.ClanAppDeclinedItem(cId, cName, cTag, appId)


class _ClanInviteActionParser(SectionParser):

    def parse(self, section):
        return self._createItem(section.readInt64('account_id'), section.readInt('invite_id'))

    def _createItem(self, account_id, invite_id):
        raise NotImplementedError


class _ClanInviteAcceptedParser(_ClanInviteActionParser):

    def getTagName(self):
        pass

    def _createItem(self, account_id, invite_id):
        return proxy_data.ClanInviteAcceptedItem(account_id, invite_id)


class _ClanInviteDeclinedParser(_ClanInviteActionParser):

    def getTagName(self):
        pass

    def _createItem(self, account_id, invite_id):
        return proxy_data.ClanInviteDeclinedItem(account_id, invite_id)


class _ClanInvitesCreatedParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        return proxy_data.ClanInvitesCreatedItem(self.__getItems('account_ids', section), self.__getItems('invite_ids', section))

    def __getItems(self, sectionName, section):
        s = self._readString(sectionName, section)
        itemsList = s.split(',')
        return tuple((long(itemsList[i].strip()) for i in xrange(len(itemsList))))


class _ShowPromoParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        data = dict(section)
        data['data'] = dict(section['data'])
        return proxy_data.ShowTeaserItem(PromoDataParser.parseXML(section))


class _ShowInBrowserParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        url = section.readString('url')
        if not url:
            _logger.error('WGNC show_in_browser item has no URL')
            return
        size = parseSize(section.readString('size'))
        title = section.readString('title')
        titleKey = section.readString('title_key')
        showRefresh = section.readBool('show_refresh')
        webClientHandler = section.readString('web_client_handler')
        isSolidBorder = section.readBool('is_solid_border')
        return proxy_data.ShowInBrowserItem(url, size, title, showRefresh, webClientHandler, titleKey=titleKey, isSolidBorder=isSolidBorder)


class _ProxyDataItemsParser(ParsersCollection):

    def getTagName(self):
        pass

    def parse(self, section):
        items = []
        for item in super(_ProxyDataItemsParser, self).parse(section):
            if item is not None:
                items.append(item)

        return proxy_data.ProxyDataHolder(items)


class _ReferralBubbleParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        return proxy_data.UpdateRefferalBubbleItem()


class _ClanNotificationParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        alias = section.readString('alias')
        value = section.readInt('count', 0)
        isIncrement = section.readBool('isIncrement', True)
        if alias:
            return proxy_data.UpdateClanNotificationItem(alias, value, isIncrement)
        _logger.warning('WGNC update_clan_news_counter item has no alias')


class _BecomeRecruiterParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        return proxy_data.BecomeRecruiterItem()


class _ShowReferralWindowParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        relativeUrl = section.readString('relative_url')
        if not relativeUrl:
            _logger.warning('WGNC show_referral_window item has no relative_url')
        return proxy_data.ShowReferralWindowItem(relativeUrl)


class _PaymentMethodChangeParser(SectionParser):
    _OPERATION_NAME = ''

    def getTagName(self):
        raise NotImplementedError

    def parse(self, section):
        method = section.readString('method')
        if not method:
            _logger.error('WGNC %s item has no method', self.getTagName())
        cdnUrl = section.readString('imageUrl')
        if not cdnUrl:
            _logger.warning('WGNC %s item has no imageUrl', self.getTagName())
        return proxy_data.PaymentMethodChangeItem(self._OPERATION_NAME, method, cdnUrl)


class _PaymentMethodLinkParser(_PaymentMethodChangeParser):
    _OPERATION_NAME = 'link'

    def getTagName(self):
        pass


class _PaymentMethodUnlinkParser(_PaymentMethodChangeParser):
    _OPERATION_NAME = 'unlink'

    def getTagName(self):
        pass


class _MapboxSurveyAvailableParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        return proxy_data.ShowMapboxSurveyAvailableMessage(section.readString('geometry_name'))


class _MapboxEventStartedParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, _):
        return proxy_data.ShowMapboxEventStartedMessage()


class _MapboxEventEndedParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, _):
        return proxy_data.ShowMapboxEventEndedMessage()


class _MapboxRewardReceivedParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        return proxy_data.ShowMapboxRewardReceivedMessage({'rewards': json.loads(section['rewards'].asString),
         'battles': section['battles'].asInt,
         'isFinal': section.readBool('is_last_reward')})


class _IntegratedAuctionRateErrorParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        return proxy_data.ShowAuctionRateErrorMessage()


class _IntegratedAuctionBelowCompetitiveRateParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        return proxy_data.ShowAuctionBelowCompetitiveRateMessage()


class _IntegratedAuctionLostRateParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        messageData = json.loads(section['data'].asString)
        return proxy_data.ShowAuctionLostRateMessage(messageData=messageData)


class ProxyDataItemParser_v2(_ProxyDataItemsParser):

    def __init__(self):
        super(ProxyDataItemParser_v2, self).__init__((_ClanApplicationParser(),
         _ClanAppAcceptedActionParser(),
         _ClanAppDeclinedActionParser(),
         _ClanInviteParser(),
         _ClanAppDeclinedParser(),
         _ClanAppAcceptedParser(),
         _ClanInvitesCreatedParser(),
         _ClanInviteDeclinedParser(),
         _ClanInviteAcceptedParser(),
         _ShowInBrowserParser(),
         _ShowPromoParser(),
         _ReferralBubbleParser(),
         _BecomeRecruiterParser(),
         _ShowReferralWindowParser(),
         _ClanNotificationParser(),
         _PaymentMethodLinkParser(),
         _PaymentMethodUnlinkParser(),
         _MapboxSurveyAvailableParser(),
         _MapboxEventStartedParser(),
         _MapboxEventEndedParser(),
         _MapboxRewardReceivedParser(),
         _IntegratedAuctionRateErrorParser(),
         _IntegratedAuctionBelowCompetitiveRateParser(),
         _IntegratedAuctionLostRateParser()))
