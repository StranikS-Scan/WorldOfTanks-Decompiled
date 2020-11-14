# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgnc/xml/actions_parsers.py
import resource_helper
from gui.wgnc import actions
from gui.wgnc.wgnc_helpers import parseSize
from gui.wgnc.errors import ParseError
from gui.wgnc.xml.shared_parsers import SectionParser, ParsersCollection

class _CallbackActionParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        return actions.Callback(self._readString('name', section), section.readBool('purge', True))


class _BrowseActionParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        name = self._readString('name', section)
        url = self._readString('href', section)
        target = section.readString('target', 'internal')
        if target == 'internal':
            size = parseSize(section.readString('size'))
            showRefresh = section.readBool('show_refresh')
            webClientHandler = section.readString('web_client_handler')
            isSolidBorder = section.readBool('is_solid_border')
            action = actions.OpenInternalBrowser(name, url, size, showRefresh, webClientHandler, isSolidBorder)
        elif target == 'external':
            action = actions.OpenExternalBrowser(name, url)
        elif target == 'promo':
            action = actions.OpenPromoBrowser(name, url)
        elif target == 'stronghold':
            action = actions.OpenStrongholdBrowser(name, url)
        else:
            raise ParseError('The target of action "{0}" is not valid: {1}.'.format(self.getTagName(), target))
        return action


class _OpenWindowParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        return actions.OpenWindow(self._readString('name', section), self._readString('target', section))


class _CustomActionsParser(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        ctx, _ = resource_helper.getRoot('')
        return actions.CustomAction(action_name=self._readString('name', section), **self.__parse(ctx, section))

    def __parse(self, ctx, section):
        res = {}
        for c, ss in resource_helper.getIterator(ctx, section):
            val = resource_helper.readItem(c, ss, ss.name).value
            res[self.__getKeyName(ss)] = val if val else self.__parse(c, ss)

        if not res:
            res[self.__getKeyName(section)] = resource_helper.readItem(ctx, section, section.name).value
        if 'action_class' not in res.keys():
            res['action_class'] = resource_helper.readItem(ctx, section, section.name).value
        return res

    def __getKeyName(self, section):
        return section['name'].asString if section['name'] is not None else section.name


class _ReplaceButtonsAction(SectionParser):

    def getTagName(self):
        pass

    def parse(self, section):
        text = section.asString
        if not text:
            raise ParseError('The content of action "{0}" is not defined.'.format(self.getTagName()))
        return actions.ReplaceButtons(self._readString('name', section), section.asString)


class _ActionsParser(ParsersCollection):

    def getTagName(self):
        pass

    def parse(self, section):
        items = []
        for item in super(_ActionsParser, self).parse(section):
            items.append(item)

        return actions.ActionsHolder(items)


class ActionsParser_v2(_ActionsParser):

    def __init__(self):
        super(ActionsParser_v2, self).__init__((_CallbackActionParser(),
         _BrowseActionParser(),
         _OpenWindowParser(),
         _ReplaceButtonsAction(),
         _CustomActionsParser()))
