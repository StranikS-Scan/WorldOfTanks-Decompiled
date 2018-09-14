# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgnc/xml/proxy_data_parsers.py
from debug_utils import LOG_ERROR
from gui.wgnc import proxy_data
from gui.wgnc.wgnc_helpers import parseSize
from gui.wgnc.xml.shared_parsers import ParsersCollection, SectionParser

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
    """
    This notification comes to clan members with appropriate rights of recruiting
    when someone from their clan sends invites
    """

    def getTagName(self):
        pass

    def parse(self, section):
        return proxy_data.ClanInvitesCreatedItem(self.__getItems('account_ids', section), self.__getItems('invite_ids', section))

    def __getItems(self, sectionName, section):
        str = self._readString(sectionName, section)
        itemsList = str.split(',')
        return tuple((long(itemsList[i].strip()) for i in xrange(len(itemsList))))


class _EncyclopediaContentParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        return proxy_data.EncyclopediaContentItem(section.readInt('content_id'))


class _ShowInBrowserParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        url = section.readString('url')
        if not url:
            LOG_ERROR('WGNC show_in_browser item has no URL')
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
         _EncyclopediaContentParser(),
         _ShowInBrowserParser()))
