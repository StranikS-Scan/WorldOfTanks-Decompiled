# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/fun_random_tactical_maps_config.py
from collections import namedtuple
from frameworks.wulf import Array
import ResMgr
MapConfig = namedtuple('MapConfig', ('mapPoints',))
MapPoint = namedtuple('MapPoint', ('id', 'typeName', 'position'))

class TacticalMapsConfig(object):

    def __init__(self, mapsData):
        super(TacticalMapsConfig, self).__init__()
        self._mapsData = mapsData

    def getMapConfig(self, geometryName):
        return self._mapsData.get(geometryName, MapConfig([]))

    def getMapsIds(self):
        return self._mapsData.keys()


class TacticalMapsConfigReader(object):

    @staticmethod
    def readXml(xmlPath):
        section = ResMgr.openSection(xmlPath)
        mapsData = dict()
        mapsSection = section['maps']
        for mapSection in mapsSection.values():
            mapId = mapSection.readString('geometryName', '')
            mapPointsSection = mapSection['mapPoints']
            mapPointsValues = mapPointsSection.values() if mapPointsSection else ()
            mapPointsData = tuple([ MapPoint(mapPointsSection.readInt('id', 0), mapPointsSection.readString('typeName', ''), mapPointsSection.readVector2('position')) for mapPointsSection in mapPointsValues ])
            mapsData[mapId] = MapConfig(mapPointsData)

        ResMgr.purge(xmlPath)
        return TacticalMapsConfig(mapsData)
