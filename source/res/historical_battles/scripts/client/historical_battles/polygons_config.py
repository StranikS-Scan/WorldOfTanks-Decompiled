# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/polygons_config.py
import ResMgr

class PolygonsConfig(object):

    def __init__(self, polygons):
        super(PolygonsConfig, self).__init__()
        self._polygons = polygons

    def getPolygon(self, polygonId):
        if not isinstance(polygonId, str):
            polygonId = str(int(polygonId))
        return self._polygons.get(polygonId, '')


class PolygonsConfigReader(object):
    FRONTMANS_PATH = 'historical_battles/gui/frontman_polygons.xml'

    @staticmethod
    def readXml(xmlPath):
        section = ResMgr.openSection(xmlPath)
        itemsData = dict()
        if section:
            itemsSection = section['items']
            for itemSection in itemsSection.values():
                itemId = itemSection.readString('id', '')
                itemsData[itemId] = itemSection.readString('points', '')

        ResMgr.purge(xmlPath)
        return PolygonsConfig(itemsData)
