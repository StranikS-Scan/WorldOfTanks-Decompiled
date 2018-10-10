# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/doc_loaders/EULAVersionLoader.py
import ResMgr
from helpers import VERSION_FILE_PATH
from soft_exception import SoftException
__author__ = 'd_savitski'
VERSION_TAG = 'showLicense'

class EULAVersionLoader(object):

    def __init__(self):
        super(EULAVersionLoader, self).__init__()
        self.__xmlVersion = 0
        self.loadXMLVersion()

    @property
    def xmlVersion(self):
        return self.__xmlVersion

    def loadXMLVersion(self):
        xmlFile = ResMgr.openSection(VERSION_FILE_PATH)
        if not xmlFile:
            raise SoftException('EULAVersionLoader.loadXMLVersion %s file is missing' % VERSION_FILE_PATH)
        xmlVersion = xmlFile.readString(VERSION_TAG)
        if not xmlVersion:
            raise SoftException('Subsection EULAVersionLoader.loadXMLVersion EULAVersion tag <%(ver)s> is missing or empty in %(path)s' % {'ver': VERSION_TAG,
             'path': VERSION_FILE_PATH})
        self.__xmlVersion = int(xmlVersion)
