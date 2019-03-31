# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/customization/data_providers.py
# Compiled at: 2018-11-29 14:33:44
from items import vehicles
from helpers import i18n
from gui.ClientHangarSpace import _CAMOUFLAGE_MIN_INTENSITY
from gui.Scaleform.data_providers import BaseDataProvider
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.utils.functions import makeTooltip
import Math
import time

class CamouflageRentalPackageDataProvider(BaseDataProvider):
    DEFAULT_RENTAL_PACKAGE_IDX = 0

    def __init__(self, prefix):
        super(CamouflageRentalPackageDataProvider, self).__init__(prefix)
        self.__list = []

    def getIndexByDays(self, days):
        findIdx = self.DEFAULT_RENTAL_PACKAGE_IDX
        for idx, (periodDays, _, _, _) in enumerate(self.__list):
            if periodDays == days:
                findIdx = idx
                break

        return findIdx

    def buildList(self, costs):
        if costs is None:
            costs = {}
        result = []
        for periodDays, (cost, isGold) in costs.iteritems():
            if periodDays > 1:
                i18nPeriodDays = i18n.makeString('#menu:customization/period/days', periodDays)
            elif periodDays == 1:
                i18nPeriodDays = i18n.makeString('#menu:customization/period/day')
            else:
                i18nPeriodDays = i18n.makeString('#menu:customization/period/infinity')
            result.append([periodDays,
             cost,
             isGold == 1,
             i18nPeriodDays])

        self.__list = sorted(result, cmp=self.__comparator, reverse=True)
        return

    def emptyItem(self):
        return [-1,
         -1,
         False,
         '']

    @property
    def list(self):
        return self.__list

    def __comparator(self, item, other):
        result = 0
        if item[0] and other[0]:
            result = cmp(item[0], other[0])
        elif item[0] != other[0]:
            result = 1 if not item[0] else -1
        return result


class CamouflageGroupsDataProvider(BaseDataProvider):

    def __init__(self, prefix):
        super(CamouflageGroupsDataProvider, self).__init__(prefix)
        self.__list = []

    def buildList(self, nationID):
        if nationID is None:
            return
        else:
            customization = vehicles.g_cache.customization(nationID)
            result = []
            if customization is not None:
                groups = customization.get('camouflageGroups', {})
                for name, info in groups.iteritems():
                    result.append([name, info.get('userString', name), info.get('hasNew', False)])

            self.__list = sorted(result, cmp=self.__comparator)
            return

    def emptyItem(self):
        return [None, '', False]

    @property
    def list(self):
        return self.__list

    def __comparator(self, item, other):
        return cmp(item[0], other[0])


class CamouflagesDataProvider(UIInterface):

    def __init__(self, prefix):
        UIInterface.__init__(self)
        self.__prefix = prefix
        self.__defCost = -1.0
        self.__isGold = 0
        self.__vehPriceFactor = 1.0
        self.currentCamouflageID = None
        return

    @classmethod
    def _makeTextureUrl(cls, width, height, texture, colors, armorColor, lifeCycle=None):
        if texture is None or len(texture) == 0:
            return ''
        else:
            weights = Math.Vector4((colors[0] >> 24) / 255.0, (colors[1] >> 24) / 255.0, (colors[2] >> 24) / 255.0, (colors[3] >> 24) / 255.0)
            if lifeCycle is not None:
                startTime, days = lifeCycle
                if days > 0:
                    timeAmount = float((time.time() - startTime) / (days * 86400))
                    if timeAmount > 1.0:
                        weights *= _CAMOUFLAGE_MIN_INTENSITY
                    elif timeAmount > 0:
                        weights *= (1.0 - timeAmount) * (1.0 - _CAMOUFLAGE_MIN_INTENSITY) + _CAMOUFLAGE_MIN_INTENSITY
            return 'img://camouflage,{0:d},{1:d},"{2:>s}",{3[0]:d},{3[1]:d},{3[2]:d},{3[3]:d},{4[0]:n},{4[1]:n},{4[2]:n},{4[3]:n},{5:d}'.format(width, height, texture, colors, weights, armorColor)

    @classmethod
    def _makeSmallTextureUrl(cls, texture, colors, armorColor, lifeCycle=None):
        return CamouflagesDataProvider._makeTextureUrl(67, 67, texture, colors, armorColor, lifeCycle=lifeCycle)

    @classmethod
    def _makeCost(cls, defCost, vehPriceFactor, camPriceFactor):
        return int(round(defCost * vehPriceFactor * camPriceFactor))

    @classmethod
    def _makeDescription(cls, groups, groupNames, description):
        result = ''
        names = []
        if description is None:
            description = ''
        if groupNames is None:
            groupNames = ''
        if len(description) > 0 and len(groupNames) > 0:
            for groupName in groupNames:
                userString = groups.get(groupName, {}).get('userString')
                if userString is not None:
                    names.append(userString)

            result = makeTooltip(header=', '.join(names), body=description)
        return result

    def makeItem(self, nationID, camouflageID, isCurrent, lifeCycle=None):
        customization = vehicles.g_cache.customization(nationID)
        groups = customization.get('camouflageGroups', {})
        if customization is not None:
            camouflage = customization.get('camouflages', {}).get(camouflageID, {})
            armorColor = customization.get('armorColor', 0)
            camouflageInfo = [camouflageID,
             self._makeSmallTextureUrl(camouflage.get('texture'), camouflage.get('colors', (0, 0, 0, 0)), armorColor, lifeCycle=lifeCycle),
             self._makeDescription(groups, camouflage.get('groupNames', ''), camouflage.get('description', '')),
             self._makeCost(self.__defCost, self.__vehPriceFactor, camouflage.get('priceFactor', 1.0)),
             self.__isGold == 1,
             camouflage.get('isNew', False),
             isCurrent]
        else:
            camouflageInfo = [camouflageID,
             None,
             '',
             0,
             False,
             False,
             isCurrent]
        return camouflageInfo

    def getCost(self, nationID, camouflageID):
        camouflage = vehicles.g_cache.customization(nationID).get('camouflages', {}).get(camouflageID, {})
        return (self._makeCost(self.__defCost, self.__vehPriceFactor, camouflage.get('priceFactor', 1.0)), self.__isGold)

    def setVehicleTypeParams(self, vehPriceFactor, camouflageID):
        self.__vehPriceFactor = vehPriceFactor
        self.currentCamouflageID = camouflageID

    def setDefaultCost(self, defCost, isGold):
        self.__defCost = defCost
        self.__isGold = isGold == 1

    def __comparator(self, item, other):
        if item[3] ^ other[3]:
            result = -1 if item[3] else 1
        else:
            result = cmp(item[0], other[0])
        return result

    def populateUI(self, proxy):
        super(CamouflagesDataProvider, self).populateUI(proxy)
        self.uiHolder.addExternalCallbacks({'{0:>s}.RequestList'.format(self.__prefix): self.onRequestList})

    def dispossessUI(self):
        self.uiHolder.removeExternalCallbacks('{0:>s}.RequestList'.format(self.__prefix))
        super(CamouflagesDataProvider, self).dispossessUI()

    def onRequestList(self, *args):
        parser = CommandArgsParser(self.onRequestList.__name__, 2, [int, str])
        nationID, groupName = parser.parse(*args)
        customization = vehicles.g_cache.customization(nationID)
        result = []
        if customization is not None:
            groups = customization.get('camouflageGroups', {})
            group = groups.get(groupName, {})
            camouflages = customization.get('camouflages', {})
            armorColor = customization.get('armorColor', 0)
            ids = group.get('ids', [])
            isGold = self.__isGold == 1
            for id in ids:
                camouflage = camouflages.get(id)
                if camouflage is not None and camouflage.get('showInShop', False):
                    texture = camouflage.get('texture')
                    colors = camouflage.get('colors', (0, 0, 0, 0))
                    result.append([id,
                     self._makeSmallTextureUrl(texture, colors, armorColor),
                     self._makeDescription(groups, camouflage.get('groupNames', ''), camouflage.get('description', '')),
                     self._makeCost(self.__defCost, self.__vehPriceFactor, camouflage.get('priceFactor', 1.0)),
                     isGold,
                     camouflage.get('isNew', False),
                     self.currentCamouflageID == id])

        for item in sorted(result, cmp=self.__comparator):
            parser.addArgs(item)

        self.respond(parser.args())
        return

    def refresh(self):
        self.uiHolder.call('{0:>s}.RefreshList'.format(self.__prefix), [True])


class HornsDataProvider(BaseDataProvider):

    def __init__(self, prefix):
        super(HornsDataProvider, self).__init__(prefix)
        self.__vehicleTags = set()
        self.__hornPriceFactor = 1.0
        self.__costs = {}
        self.__list = []

    @classmethod
    def _makeCost(cls, defCost, priceFactor):
        return int(round(defCost * priceFactor))

    def getCost(self, hornID):
        return self._makeCost(self.__costs.get(hornID, 0), self.__hornPriceFactor)

    def makeItem(self, hornID, isCurrent):
        horn = vehicles.g_cache.horns().get(hornID, {})
        return [hornID,
         horn.get('userString', ''),
         self.getCost(hornID),
         isCurrent]

    def setVehicleTypeParams(self, vehicleTags, hornPriceFactor):
        self.__vehicleTags = vehicleTags
        self.__hornPriceFactor = hornPriceFactor

    def setHornDefCosts(self, costs):
        self.__costs = costs

    def buildList(self, currentHornID):
        horns = vehicles.g_cache.horns()
        result = []
        if horns is not None:
            for id, info in horns.iteritems():
                allowedTags = info.get('vehicleTags', set())
                if self.__vehicleTags & allowedTags:
                    result.append([id,
                     info.get('userString', ''),
                     self.getCost(id),
                     currentHornID == id])

        self.__list = sorted(result, cmp=lambda item, other: cmp(item[1], other[1]))
        return

    def emptyItem(self):
        return [None,
         '',
         0,
         False]

    @property
    def list(self):
        return self.__list
