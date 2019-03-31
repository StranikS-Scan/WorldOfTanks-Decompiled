# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/EULA.py
# Compiled at: 2018-11-29 14:33:44
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
import BigWorld, ResMgr
from gui import EULA_FILE_PATH, VERSION_FILE_PATH
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from gui.Scaleform.windows import UIInterface
SHOW_LICENCE_TAG = 'showLicense'

class EULAInterface(UIInterface):
    __showLicense = False
    __licenseText = []

    def __init__(self):
        super(EULAInterface, self).__init__()
        self.__readVersionFile()
        if self.__showLicense:
            self.__readEULAFile()

    def isShowLicense(self):
        return self.__showLicense and len(self.__licenseText) > 0

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.addExternalCallbacks({'EULA.GetLicenseText': self.onGetLicenseText,
         'EULA.OpenWebBrowser': self.onOpenWebBrowser,
         'EULA.Agree': self.onPlayerAgree})

    def dispossessUI(self):
        self.uiHolder.removeExternalCallbacks('EULA.GetLicenseText', 'EULA.OpenWebBrowser', 'EULA.Agree')
        UIInterface.dispossessUI(self)

    def __readEULAFile(self):
        dSection = ResMgr.openSection(EULA_FILE_PATH)
        if dSection is None:
            LOG_ERROR('Can not open file:', EULA_FILE_PATH)
            self.__showLicense = False
            return
        else:
            try:
                processor = _LicenseXMLProcessor()
                for child in dSection.values():
                    result = processor.execute(child, result=[])
                    if len(result) > 0:
                        self.__licenseText.extend(result)

            except Exception:
                LOG_CURRENT_EXCEPTION()
                self.__licenseText = []

            ResMgr.purge(EULA_FILE_PATH, True)
            return

    def __readVersionFile(self):
        dSection = ResMgr.openSection(VERSION_FILE_PATH)
        if dSection is None:
            LOG_ERROR('Can not open file:', VERSION_FILE_PATH)
            self.__showLicense = False
            return
        else:
            self.__showLicense = bool(dSection.readInt(SHOW_LICENCE_TAG, 0))
            return

    def __saveVersionFile(self):
        dSection = ResMgr.openSection(VERSION_FILE_PATH)
        if dSection is None:
            LOG_ERROR('Can not open file:', VERSION_FILE_PATH)
            self.__showLicense = False
            return
        else:
            dSection.writeInt(SHOW_LICENCE_TAG, 0)
            isReleaseVer = False
            try:
                f = open(VERSION_FILE_PATH, 'rb')
                f.close()
            except IOError:
                isReleaseVer = True

            f = open('version.xml' if isReleaseVer else VERSION_FILE_PATH, 'wb')
            f.write(dSection.asBinary)
            f.close()
            return

    def onGetLicenseText(self, *args):
        for text in self.__licenseText:
            self.call('EULA.AppendLicenseText', [text])

    def onOpenWebBrowser(self, *args):
        parser = CommandArgsParser(self.onGetLicenseText.__name__, 1, [str])
        url = parser.parse(*args)
        BigWorld.wg_openWebBrowser(url)

    def onPlayerAgree(self, *args):
        self.__saveVersionFile()


EULA_TEMPLATES_FILE_PATH = 'gui/EULA_templates.xml'

class _TagTemplate(object):

    def __init__(self, template):
        self._template = template

    def execute(self, section, processor, result):
        result.append(self._template)


class _LinkTemplate(_TagTemplate):

    def execute(self, section, processor, result):
        name = section['name'].asWideString if section.has_key('name') else section.asWideString
        url = section['url'].asWideString if section.has_key('url') else section.asWideString
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

    def execute(self, section, processor=None, result=None):
        template = self.__templates.get(section.name)
        if result is None:
            result = []
        if template is not None:
            template.execute(section, self, result)
        else:
            result.append(section.asWideString)
        return result
