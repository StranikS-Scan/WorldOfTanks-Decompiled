# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BootcampParser.py
import ResMgr
from items import _xml
from debug_utils_bootcamp import LOG_ERROR_BOOTCAMP
from BootcampContext import AreaMarker

def _parseID(xmlCtx, section, msg):
    entityID = section.asString
    if not entityID:
        _xml.raiseWrongXml(xmlCtx, section.name, msg)
    return entityID


def _readModelMarkerSection(xmlCtx, section, name='model'):
    result = {}
    if name in section.keys():
        subSec = _xml.getSubsection(xmlCtx, section, name)
        result = {'path': _xml.readString(xmlCtx, subSec, 'path'),
         'action': _xml.readString(xmlCtx, subSec, 'action'),
         'offset': _xml.readVector3(xmlCtx, subSec, 'offset')}
    return result


def _readWorldMarkerSection(xmlCtx, section):
    subSec = _xml.getSubsection(xmlCtx, section, 'world')
    return {'shape': _xml.readString(xmlCtx, subSec, 'shape'),
     'min-distance': _xml.readFloat(xmlCtx, subSec, 'min-distance'),
     'max-distance': _xml.readFloat(xmlCtx, subSec, 'max-distance'),
     'offset': _xml.readVector3(xmlCtx, subSec, 'offset')}


def _readAreaMarkerSection(xmlCtx, section, markerID):
    return AreaMarker(markerID, _readModelMarkerSection(xmlCtx, section), _readModelMarkerSection(xmlCtx, section, name='ground'), _readWorldMarkerSection(xmlCtx, section), createInd=section.readBool('create-indicator', True))


_MARKER_TYPES = {'Area': _readAreaMarkerSection}

def _readMarkerSection(xmlCtx, section, _):
    markerID = _parseID(xmlCtx, section, 'Specify a marker ID')
    type = _xml.readString(xmlCtx, section, 'type')
    marker = None
    if type in _MARKER_TYPES:
        parser = _MARKER_TYPES[type]
        marker = parser(xmlCtx, section, markerID)
    else:
        LOG_ERROR_BOOTCAMP('Marker is not supported:', type)
    return marker


_BASE_ENTITY_PARSERS = {'marker': _readMarkerSection}
_ENTITY_PARSERS = _BASE_ENTITY_PARSERS.copy()

def _parseEntity(xmlCtx, name, section, flags):
    parser = _ENTITY_PARSERS.get(name)
    item = None
    if parser is not None:
        item = parser(xmlCtx, section, flags)
    else:
        LOG_ERROR_BOOTCAMP('Entity is not supported:', name)
    return item


class BootcampParser(object):

    @staticmethod
    def parse(chapter):
        filePath = chapter.getFilePath()
        section = ResMgr.openSection(filePath)
        if section is None:
            _xml.raiseWrongXml(None, filePath, 'can not open or read')
        xmlCtx = (None, filePath)
        flags = []
        BootcampParser._parseEntities(xmlCtx, section, flags, chapter)
        return

    @staticmethod
    def _parseEntities(xmlCtx, section, flags, chapter):
        for name, subSec in _xml.getChildren(xmlCtx, section, 'has-id'):
            entity = _parseEntity(xmlCtx, name, subSec, flags)
            if entity is not None:
                chapter.addEntity(entity)

        return
