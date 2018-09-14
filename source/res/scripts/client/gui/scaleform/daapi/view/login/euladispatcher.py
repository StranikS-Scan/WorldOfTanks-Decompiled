# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/EULADispatcher.py
import ResMgr
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_CURRENT_EXCEPTION
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.doc_loaders.EULAVersionLoader import EULAVersionLoader
from gui.shared import EVENT_BUS_SCOPE
from helpers import getClientLanguage
from gui import makeHtmlString, GUI_SETTINGS
from gui.shared.events import CloseWindowEvent, LoadViewEvent
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from Event import Event
from adisp import async
VERSION_TAG = 'showLicense'
EULA_TEMPLATES_FILE_PATH = 'gui/EULA_templates.xml'
EULA_FILE_PATH = 'text/EULA.xml'

class EULADispatcher(EventSystemEntity):
    onEULAClosed = Event()

    def __init__(self):
        super(EULADispatcher, self).__init__()
        self.serverVersion = None
        self.isShow = False
        self.EULACallback = None
        self.EULAVersion = EULAVersionLoader()
        return

    def _populate(self):
        EventSystemEntity._populate(self)
        if self.isShow == False:
            return
        isShowFullEULA = GUI_SETTINGS.eula.full
        if isShowFullEULA:
            self.__eulaText = self.__readEULAFull()
            if not len(self.__eulaText):
                isShowFullEULA = False
        if not isShowFullEULA:
            self.__eulaText = self.__readEULAShort()
        if len(self.__eulaText):
            self.addListener(CloseWindowEvent.EULA_CLOSED, self.__onEulaClosed)
            self.fireEvent(LoadViewEvent(VIEW_ALIAS.EULA_FULL if isShowFullEULA else VIEW_ALIAS.EULA, ctx={'text': self.__eulaText}), EVENT_BUS_SCOPE.LOBBY)

    def __onEulaClosed(self, event):
        self.onEULAClosed()
        if event.isAgree:
            self.__saveVersionFile()

    @async
    def processLicense(self, callback = None):
        self.EULACallback = callback
        from account_helpers.AccountSettings import AccountSettings, EULA_VERSION
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        defaults = AccountSettings.getFilterDefault(EULA_VERSION)
        filters = g_settingsCore.serverSettings.getSection(EULA_VERSION, defaults)
        self.serverVersion = int(filters['version'])
        self.isShow = False
        xmlVersion = self.EULAVersion.xmlVersion
        if self.serverVersion != xmlVersion and xmlVersion != 0:
            self.isShow = True
        if self.isShow:
            Waiting.close()
            self.create()
        else:
            callback(True)

    def __saveVersionFile(self):
        self.__showLicense = False
        from account_helpers.AccountSettings import EULA_VERSION
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        version = {'version': self.EULAVersion.xmlVersion}
        g_settingsCore.serverSettings.setSection(EULA_VERSION, version)
        self.serverVersion = None
        self.EULACallback(True)
        return

    def __readEULAShort(self):
        return makeHtmlString('html_templates:lobby/dialogs', 'eula', {'eulaURL': GUI_SETTINGS.eula.url.format(getClientLanguage())})

    def __readEULAFull(self):
        if not GUI_SETTINGS.eula.full:
            return ''
        else:
            dSection = ResMgr.openSection(EULA_FILE_PATH)
            text = []
            if dSection is None:
                LOG_WARNING('Can not open file:', EULA_FILE_PATH)
                self.__showLicense = False
                return ''
            try:
                processor = _LicenseXMLProcessor()
                for child in dSection.values():
                    result = processor.execute(child, result=[])
                    if len(result) > 0:
                        text.extend(result)

            except Exception:
                LOG_CURRENT_EXCEPTION()

            return ''.join(text)

    def fini(self):
        self.removeListener(CloseWindowEvent.EULA_CLOSED, self.__onEulaClosed)
        self.serverVersion = None
        self.isShow = None
        self.EULACallback = None
        self.EULAVersion = None
        self.destroy()
        return


class _TagTemplate(object):

    def __init__(self, template):
        self._template = template

    def execute(self, section, processor, result):
        result.append(self._template)


class _LinkTemplate(_TagTemplate):

    def execute(self, section, processor, result):
        name = section['name'].asWideString if section.has_key('name') else section.asWideString
        if section.has_key('url'):
            if section['url'].asWideString == '#eulaUrl':
                lng = getClientLanguage()
                url = GUI_SETTINGS.eula.url.format(lng)
            else:
                url = section['url'].asWideString
        else:
            url = section.asWideString
        result.append(self._template % (url, name))


class _TitleTemplate(_TagTemplate):

    def execute(self, section, processor, result):
        result.append(self._template % section.asWideString)


class _ContentTemplate(_TagTemplate):

    def execute(self, section, processor, result):
        values = section.values()
        if len(values) > 0:
            selfResult = []
            for tSection in values:
                processor.execute(tSection, processor, selfResult)

        else:
            selfResult = [section.asWideString]
        result.append(self._template % u''.join(selfResult))


class _ChapterTemplate(object):

    def __init__(self, titleTemplate, contentTemplate):
        self.__title = _TitleTemplate(titleTemplate)
        self.__content = _ContentTemplate(contentTemplate)

    def execute(self, section, processor, result):
        tSection = section['title']
        if tSection is not None:
            self.__title.execute(tSection, processor, result)
        cSection = section['content']
        if cSection is not None:
            self.__content.execute(cSection, processor, result)
        return


class _LicenseXMLProcessor(object):
    __templates = {}

    def __init__(self):
        self.__loadTemplates()

    def __loadTemplates(self):
        dSection = ResMgr.openSection(EULA_TEMPLATES_FILE_PATH)
        if dSection is None:
            LOG_ERROR('Can not open file:', EULA_TEMPLATES_FILE_PATH)
        for tagName, child in dSection.items():
            className = child.readString('class')
            if className is None:
                continue
            clazz = globals().get(className)
            if clazz is None:
                LOG_ERROR('Not found class:', clazz)
                continue
            args = []
            argsSection = child['args'] if child.has_key('args') else []
            for argSection in argsSection.values():
                arg = argSection.asString
                if len(arg) > 0:
                    args.append(arg)

            self.__templates[tagName] = clazz(*args)

        return

    def execute(self, section, processor = None, result = None):
        template = self.__templates.get(section.name)
        if result is None:
            result = []
        if template is not None:
            template.execute(section, self, result)
        else:
            result.append(section.asWideString)
        return result
