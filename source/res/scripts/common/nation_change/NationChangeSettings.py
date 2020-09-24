# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/nation_change/NationChangeSettings.py
from typing import List, Dict, Iterable
from realm_utils import ResMgr
from items import _xml

class NationGroup(object):
    __slots__ = ('ID', 'tankList')

    def __init__(self, ID):
        self.ID = ID
        self.tankList = []


class NationChangeSettings(object):

    def __init__(self, xmlPath):
        self.__groupById = self.__readSettings(xmlPath)

    def getGroupById(self, groupId):
        return self.__groupById.get(groupId)

    def findVehicleGroup(self, vehicleTypeName):
        for groupId, group in self.__groupById.iteritems():
            if vehicleTypeName in group.tankList:
                return group

        return None

    def iterGroups(self):
        return self.__groupById.itervalues()

    @staticmethod
    def __readSettings(xmlPath):
        configXml = ResMgr.openSection(xmlPath)
        if configXml is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        xmlCtx = (None, xmlPath)
        unique = set()
        resDict = {}
        for id_, childSection in enumerate(_xml.getChildren(xmlCtx, configXml, 'nation_groups')):
            _, changeableVehicles = childSection
            for vehicle in changeableVehicles.values():
                vehicleType = vehicle.asString
                if vehicleType in unique:
                    ctx = (xmlCtx, 'group')
                    _xml.raiseWrongXml(ctx, '', '%s is not unique' % (vehicleType,))
                    continue
                unique.add(vehicleType)
                nationGroup = resDict.setdefault(id_, NationGroup(id_))
                nationGroup.tankList.append(vehicleType)

        ResMgr.purge(xmlPath, True)
        return resDict
