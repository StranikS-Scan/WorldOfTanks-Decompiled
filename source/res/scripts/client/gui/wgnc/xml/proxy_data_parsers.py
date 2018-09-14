# Embedded file name: scripts/client/gui/wgnc/xml/proxy_data_parsers.py
from gui.wgnc import proxy_data
from gui.wgnc.xml.shared_parsers import ParsersCollection, SectionParser

class _ClanApplicationParser(SectionParser):

    def getTagName(self):
        return 'clan_application_received'

    def parse(self, section):
        return proxy_data.ClanApplicationItem(section.readInt('account_id'), section.readInt('application_id'), section.readInt('active_applications_count'))


class _ClanInviteParser(SectionParser):

    def getTagName(self):
        return 'clan_invite_received'

    def parse(self, section):
        return proxy_data.ClanInviteItem(section.readInt('invite_id'), section.readInt('clan_id'), self._readString('clan_name', section), self._readString('clan_tag', section), section.readInt('active_invites_count'))


class _ClanPersonalAppParser(SectionParser):

    def parse(self, section):
        return self._createItem(section.readInt('clan_id'), self._readString('clan_name', section), self._readString('clan_tag', section), section.readInt('application_id'))

    def _createItem(self, cId, cName, cTag, appId):
        raise NotImplementedError


class _ClanAppAcceptedParser(_ClanPersonalAppParser):

    def getTagName(self):
        return 'clan_application_accepted'

    def _createItem(self, cId, cName, cTag, appId):
        return proxy_data.ClanAppAcceptedItem(cId, cName, cTag, appId)


class _ClanAppDeclinedParser(_ClanPersonalAppParser):

    def getTagName(self):
        return 'clan_application_declined'

    def _createItem(self, cId, cName, cTag, appId):
        return proxy_data.ClanAppDeclinedItem(cId, cName, cTag, appId)


class _ClanInviteActionParser(SectionParser):

    def parse(self, section):
        return self._createItem(section.readInt('account_id'), section.readInt('invite_id'))

    def _createItem(self, account_id, invite_id):
        raise NotImplementedError


class _ClanInviteAcceptedParser(_ClanInviteActionParser):

    def getTagName(self):
        return 'clan_invite_accepted'

    def _createItem(self, account_id, invite_id):
        return proxy_data.ClanInviteAcceptedItem(account_id, invite_id)


class _ClanInviteDeclinedParser(_ClanInviteActionParser):

    def getTagName(self):
        return 'clan_invite_declined'

    def _createItem(self, account_id, invite_id):
        return proxy_data.ClanInviteDeclinedItem(account_id, invite_id)


class _ProxyDataItemsParser(ParsersCollection):

    def getTagName(self):
        return 'proxy_data'

    def parse(self, section):
        items = []
        for item in super(_ProxyDataItemsParser, self).parse(section):
            items.append(item)

        return proxy_data.ProxyDataHolder(items)


class ProxyDataItemParser_v2(_ProxyDataItemsParser):

    def __init__(self):
        super(ProxyDataItemParser_v2, self).__init__((_ClanApplicationParser(),
         _ClanInviteParser(),
         _ClanAppDeclinedParser(),
         _ClanAppAcceptedParser(),
         _ClanInviteDeclinedParser(),
         _ClanInviteAcceptedParser()))
