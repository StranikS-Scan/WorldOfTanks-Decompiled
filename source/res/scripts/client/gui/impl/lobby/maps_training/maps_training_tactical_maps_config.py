# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/maps_training/maps_training_tactical_maps_config.py
from collections import namedtuple
import ResMgr
from maps_training_common.maps_training_constants import VEHICLE_CLASSES_ORDER
MapConfig = namedtuple('MapConfig', ('teams', 'scenarios'))
Team = namedtuple('Team', ('position', 'tooltipImage', 'isLeft', 'scenarioPoints'))
Point = namedtuple('Point', ('id', 'textKeys', 'position', 'tooltipImage', 'isLeft'))
Scenario = namedtuple('Scenario', ('team', 'vehicleType'))
_BASE_OFFSET = (24, 24)
_POINT_OFFSET = (6, 6)

class TacticalMapsConfig(object):

    def __init__(self, mapsData):
        super(TacticalMapsConfig, self).__init__()
        self._mapsData = mapsData

    def getMapConfig(self, geometryName):
        return self._mapsData.get(geometryName, MapConfig({}, []))


class TacticalMapsConfigReader(object):

    @staticmethod
    def readXml(xmlPath):
        section = ResMgr.openSection(xmlPath)
        mapsData = dict()
        mapsSection = section['maps']
        for mapSection in mapsSection.values():
            mapId = mapSection.readString('geometryName', '')
            scenarios = []
            teamsData = dict()
            teamsSection = mapSection['teams']
            for teamSection in teamsSection.values():
                teamId = teamSection.readInt('id', 0)
                teamPosition = teamSection.readVector2('position') + _BASE_OFFSET
                teamTooltipImage = teamSection.readString('tooltipImage', '')
                teamIsLeft = teamSection.readBool('isLeft', False)
                scenarioPoints = dict()
                configsSection = teamSection['configs']
                for configSection in configsSection.values():
                    vehicleType = configSection.readString('type', '')
                    scenarios.append(Scenario(teamId, vehicleType))
                    pointsSection = configSection['points']
                    if not pointsSection:
                        scenarioPoints[vehicleType] = tuple()
                        continue
                    scenarioPoints[vehicleType] = tuple([ Point(pointSection.readString('id', ''), pointSection.readString('textKeys', '').split(), pointSection.readVector2('position') + _POINT_OFFSET, pointSection.readString('tooltipImage', ''), pointSection.readBool('isLeft', False)) for pointSection in pointsSection.values() ])

                teamsData[teamId] = Team(teamPosition, teamTooltipImage, teamIsLeft, scenarioPoints)

            scenarios = sorted(scenarios, key=lambda scenario: VEHICLE_CLASSES_ORDER.index(scenario.vehicleType))
            mapsData[mapId] = MapConfig(teamsData, scenarios)

        ResMgr.purge(xmlPath)
        return TacticalMapsConfig(mapsData)
