# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/detachment/images.py
import typing
import ResMgr
from items import _xml
import nations

class DetachmentImages(object):

    def __init__(self, configPath):
        self._crewImages = {}
        self._load(configPath)

    def getCrewImage(self, nationID):
        return self._crewImages.get(nationID)

    def _load(self, path):
        section = ResMgr.openSection(path)
        if section is None:
            _xml.raiseWrongSection(path, 'can not open or read')
        xmlCtx = (None, path)
        self._loadCrewImages(xmlCtx, section)
        ResMgr.purge(path)
        return

    def _loadCrewImages(self, xmlCtx, section):
        for _, itemSec in _xml.getChildren(xmlCtx, section, 'crewImages'):
            nation = _xml.readString(xmlCtx, itemSec, 'nation')
            nationID = nations.INDICES[nation]
            image = _xml.readString(xmlCtx, itemSec, 'image')
            self._crewImages[nationID] = image
