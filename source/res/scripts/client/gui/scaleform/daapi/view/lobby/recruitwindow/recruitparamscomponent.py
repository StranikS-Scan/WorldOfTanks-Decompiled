# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/recruitWindow/RecruitParamsComponent.py
import logging
import constants
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.meta.RecruitParametersMeta import RecruitParametersMeta
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from items.components import skills_constants
from items.tankmen import getSkillsConfig
from helpers.i18n import convert
from gui import GUI_NATIONS
import nations
from gui.Scaleform.locale.MENU import MENU
import Event
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
DEFAULT_NATION = -1
DEFAULT_CLASS = ''
DEFAULT_VEHICLE = -1
DEFAULT_ROLE = ''

def packPredefinedTmanParams(nationsParam, roles):
    tmanParams = {}
    if roles:
        tmanParams['roles'] = roles
    if nationsParam:
        tmanParams['nations'] = nationsParam
    return tmanParams


def _packItemVO(itemId, label):
    return {'id': itemId,
     'label': label}


class RecruitParamsComponent(RecruitParametersMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(RecruitParamsComponent, self).__init__()
        self.onDataChange = Event.Event()
        self.__selectedNationIdx = DEFAULT_NATION
        self.__selectedVehClass = DEFAULT_CLASS
        self.__selectedVehicle = DEFAULT_VEHICLE
        self.__selectedTmanRole = DEFAULT_ROLE
        self.__predefinedNations = None
        self.__predefinedNationsIdxs = None
        self.__predefinedTmanRoles = None
        self.__predefinedNationName = None
        self.__predefinedNationIdx = None
        self.__predefinedTmanRole = None
        self.__filteredNations = None
        self.__filteredVehClasses = None
        self.__filteredVehicles = None
        return

    def init(self):
        Waiting.show('updating')
        self.__setNationsData()
        self.__setVehicleClassesData()
        self.as_setVehicleDataS(self.__getSendingData([self.__getVehicleEmptyRow()], False, 0))
        self.__setEmptyTankmanRole()
        Waiting.hide('updating')
        self.onDataChange(self.__selectedNationIdx, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)

    def setPredefinedTankman(self, predefinedTmanParams):
        unsortedNations = predefinedTmanParams.get('nations', None)
        self.__predefinedNations = self.__sortNations(unsortedNations) if unsortedNations else unsortedNations
        self.__predefinedTmanRoles = predefinedTmanParams.get('roles', None)
        if self.__predefinedNations is not None:
            self.__predefinedNationsIdxs = []
            for nationName in self.__predefinedNations:
                self.__predefinedNationsIdxs.append(nations.INDICES[nationName])

            self.__predefinedNationName = self.__predefinedNations[0]
        if self.__hasPredefinedNations():
            if self.__predefinedNationName in GUI_NATIONS:
                self.__predefinedNationIdx = nations.INDICES[self.__predefinedNationName]
            self.__setNationsData()
            self.onNationChanged(self.__predefinedNationIdx)
        self.__clearFilteredData()
        if self.__hasPredefinedTmanRoles():
            self.__predefinedTmanRole = self.__predefinedTmanRoles[0]
            self.__collectPredefinedRoleData()
            if self.__predefinedTmanRole in skills_constants.ROLES:
                self.__selectedTmanRole = self.__predefinedTmanRole
                if len(self.__predefinedTmanRoles) > 1 or self.__predefinedTmanRole != 'commander':
                    if not self.__hasPredefinedNations():
                        self.onNationChanged(0)
            else:
                _logger.error('Wrong default tankman role!')
        return

    def onNationChanged(self, nationID):
        if self.__selectedNationIdx == nationID:
            return
        Waiting.show('updating')
        self.__selectedNationIdx = nationID
        self.__setVehicleClassesData()
        self.as_setVehicleDataS(self.__getSendingData([self.__getVehicleEmptyRow()], False, 0))
        self.__setEmptyTankmanRole()
        Waiting.hide('updating')
        self.onDataChange(self.__selectedNationIdx, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)

    def onVehicleClassChanged(self, vehClass):
        if self.__selectedVehClass == vehClass:
            return
        Waiting.show('updating')
        self.__selectedVehClass = vehClass
        self.__setVehicleData()
        self.__setEmptyTankmanRole()
        Waiting.hide('updating')
        self.onDataChange(self.__selectedNationIdx, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)

    def onVehicleChanged(self, vehID):
        if self.__selectedVehicle == vehID:
            return
        Waiting.show('updating')
        self.__selectedVehicle = vehID
        self.__setTankmenData()
        Waiting.hide('updating')
        self.onDataChange(self.__selectedNationIdx, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)

    def onTankmanRoleChanged(self, tManID):
        if self.__selectedTmanRole == tManID:
            return
        self.__selectedTmanRole = tManID
        self.onDataChange(self.__selectedNationIdx, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)

    def _dispose(self):
        self.onDataChange.clear()
        self.__clearFilteredData()
        super(RecruitParamsComponent, self)._dispose()

    def __setNationsData(self):
        vehsItems = self.itemsCache.items.getVehicles(self.__getNationsCriteria())
        data = []
        if self.__hasPredefinedNations():
            if vehsItems.filter(REQ_CRITERIA.NATIONS(self.__predefinedNationsIdxs)):
                for i, nation in zip(self.__predefinedNationsIdxs, self.__predefinedNations):
                    data.append(_packItemVO(i, MENU.nations(nation)))

            else:
                data.append(_packItemVO(DEFAULT_NATION, ''))
                _logger.error('Wrong nation set as default!')
            self.as_setNationsDataS(self.__getSendingData(data, len(data) > 1, 0))
        else:
            selectedNationIndex = 0
            counter = 0
            if self.__filteredNations is not None:
                data = self.__filteredNations.values()
                for nationData in data:
                    if self.__selectedNationIdx == DEFAULT_NATION:
                        self.__selectedNationIdx = nationData['id']
                    if nationData['id'] == self.__selectedNationIdx:
                        selectedNationIndex = counter
                    counter += 1

            else:
                for name in GUI_NATIONS:
                    nationIdx = nations.INDICES[name]
                    if name in nations.AVAILABLE_NAMES and vehsItems.filter(REQ_CRITERIA.NATIONS([nationIdx])):
                        if self.__selectedNationIdx == DEFAULT_NATION:
                            self.__selectedNationIdx = nationIdx
                        data.append(_packItemVO(nationIdx, MENU.nations(name)))
                        if nationIdx == self.__selectedNationIdx:
                            selectedNationIndex = counter
                        counter += 1

            self.as_setNationsDataS(self.__getSendingData(data, len(data) > 1, selectedNationIndex))
        return

    def __setVehicleClassesData(self):
        if self.__filteredVehClasses is not None:
            data = self.__filteredVehClasses[self.__selectedNationIdx]
            self.as_setVehicleClassDataS(self.__getSendingData(data, len(data) > 1, 0))
        else:
            modulesAll = self.itemsCache.items.getVehicles(self.__getClassesCriteria(self.__selectedNationIdx)).values()
            classes = []
            data = [self.__getVehicleClassEmptyRow()]
            modulesAll.sort()
            for module in modulesAll:
                if module.type in classes:
                    continue
                classes.append(module.type)
                data.append(_packItemVO(module.type, DIALOGS.recruitwindow_vehicleclassdropdown(module.type)))

            self.as_setVehicleClassDataS(self.__getSendingData(data, len(data) > 1, 0))
        return

    def __setVehicleData(self):
        selectedIndex = 0
        if self.__filteredVehicles is not None:
            if self.__selectedVehClass == DEFAULT_CLASS:
                data = [self.__getVehicleEmptyRow()]
            else:
                data = self.__filteredVehicles[self.__selectedNationIdx, self.__selectedVehClass]
                if self.__selectedVehicle != DEFAULT_VEHICLE:
                    idx = 0
                    for vehicleData in data:
                        if self.__selectedVehicle == vehicleData['id']:
                            selectedIndex = idx
                        idx += 1

            self.as_setVehicleDataS(self.__getSendingData(data, len(data) > 1, selectedIndex))
        else:
            modulesAll = self.itemsCache.items.getVehicles(self.__getVehicleTypeCriteria(self.__selectedNationIdx, self.__selectedVehClass)).values()
            data = [self.__getVehicleEmptyRow()]
            modulesAll.sort()
            for i, module in enumerate(modulesAll):
                data.append(_packItemVO(module.innationID, module.shortUserName))
                if module.innationID == self.__selectedVehicle:
                    selectedIndex = i

            self.as_setVehicleDataS(self.__getSendingData(data, len(data) > 1, selectedIndex))
        return

    def __setEmptyTankmanRole(self):
        if self.__hasPredefinedTmanRoles() and len(self.__predefinedTmanRoles) == 1:
            self.__setTankmenData()
        else:
            self.as_setTankmanRoleDataS(self.__getSendingData([self.__getTankmanRoleEmptyRow()], False, 0))

    def __setTankmenData(self):
        skillsConfig = getSkillsConfig()
        hasRoles = self.__hasPredefinedTmanRoles()
        if hasRoles and len(self.__predefinedTmanRoles) == 1:
            data = []
            for roleName in self.__predefinedTmanRoles:
                data.append(_packItemVO(roleName, convert(skillsConfig.getSkill(roleName).userString)))

            selectedIndex = 0
        else:
            modulesAll = self.itemsCache.items.getVehicles(self.__getRoleCriteria(self.__selectedNationIdx, self.__selectedVehClass, self.__selectedVehicle)).values()
            roles = []
            data = [self.__getTankmanRoleEmptyRow()]
            modulesAll.sort()
            selectedIndex = 0
            counter = 0
            for module in modulesAll:
                for role in module.descriptor.type.crewRoles:
                    roleName = role[0]
                    if roleName in roles:
                        continue
                    if not hasRoles or roleName in self.__predefinedTmanRoles:
                        roles.append(roleName)
                        data.append(_packItemVO(roleName, convert(skillsConfig.getSkill(roleName).userString)))
                        if self.__selectedTmanRole == roleName:
                            selectedIndex = counter
                    counter += 1

        self.as_setTankmanRoleDataS(self.__getSendingData(data, len(data) > 1, selectedIndex))

    def __getSendingData(self, data, enabled, selectedIndex):
        return {'enabled': enabled,
         'selectedIndex': selectedIndex,
         'data': data}

    def __getNationsCriteria(self):
        return REQ_CRITERIA.UNLOCKED | ~REQ_CRITERIA.VEHICLE.OBSERVER | ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE

    def __getVehicleTypeCriteria(self, nationID, vclass):
        criteria = self.__getClassesCriteria(nationID) | REQ_CRITERIA.VEHICLE.CLASSES([vclass])
        criteria |= ~REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
        criteria |= ~(REQ_CRITERIA.SECRET | ~REQ_CRITERIA.INVENTORY_OR_UNLOCKED)
        if not constants.IS_IGR_ENABLED:
            criteria |= ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
        if constants.IS_DEVELOPMENT:
            criteria |= ~REQ_CRITERIA.VEHICLE.IS_BOT
        return criteria

    def __getClassesCriteria(self, nationID):
        return self.__getNationsCriteria() | REQ_CRITERIA.NATIONS([nationID])

    def __getRoleCriteria(self, nationID, vclass, typeID):
        return self.__getVehicleTypeCriteria(nationID, vclass) | REQ_CRITERIA.INNATION_IDS([typeID])

    def __getVehicleClassEmptyRow(self):
        return _packItemVO(DEFAULT_CLASS, DIALOGS.RECRUITWINDOW_MENUEMPTYROW)

    def __getVehicleEmptyRow(self):
        return _packItemVO(DEFAULT_VEHICLE, DIALOGS.RECRUITWINDOW_MENUEMPTYROW)

    def __getTankmanRoleEmptyRow(self):
        return _packItemVO(DEFAULT_ROLE, DIALOGS.RECRUITWINDOW_MENUEMPTYROW)

    def __collectPredefinedRoleData(self):
        criteria = self.__getNationsCriteria()
        selectedNationsIds = []
        if self.__hasPredefinedNations():
            selectedNationsIds = self.__predefinedNationsIdxs
        else:
            for nId in nations.INDICES.itervalues():
                selectedNationsIds.append(nId)

        criteria |= REQ_CRITERIA.NATIONS(selectedNationsIds)
        if not constants.IS_IGR_ENABLED:
            criteria |= ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
        if constants.IS_DEVELOPMENT:
            criteria |= ~REQ_CRITERIA.VEHICLE.IS_BOT
        criteria |= ~(REQ_CRITERIA.SECRET | ~REQ_CRITERIA.INVENTORY_OR_UNLOCKED)
        modulesAll = self.itemsCache.items.getVehicles(criteria=criteria).values()
        modulesAll.sort()
        self.__filteredNations = dict()
        self.__filteredVehClasses = dict()
        self.__filteredVehClasses.setdefault(DEFAULT_NATION, [self.__getVehicleClassEmptyRow()])
        self.__filteredVehicles = dict()
        filteredVehClassesByNation = dict()
        count = 0
        for module in modulesAll:
            roleFound = False
            for role in module.descriptor.type.crewRoles:
                if not roleFound and role[0] in self.__predefinedTmanRoles:
                    roleFound = True
                    nationID, _ = module.descriptor.type.id
                    self.__filteredNations.setdefault(nationID, _packItemVO(nationID, MENU.nations(nations.NAMES[nationID])))
                    vehicleClassesSet = filteredVehClassesByNation.setdefault(nationID, set())
                    self.__filteredVehClasses.setdefault(DEFAULT_NATION, [self.__getVehicleClassEmptyRow()])
                    currentType = module.type
                    if currentType not in vehicleClassesSet:
                        vehicleClassesSet.add(module.type)
                        vehClasses = self.__filteredVehClasses.setdefault(nationID, [self.__getVehicleClassEmptyRow()])
                        vehClasses.append(_packItemVO(currentType, DIALOGS.recruitwindow_vehicleclassdropdown(currentType)))
                    vehicles = self.__filteredVehicles.setdefault((nationID, currentType), [self.__getVehicleEmptyRow()])
                    vehicles.append(_packItemVO(module.innationID, module.shortUserName))
                    count += 1

        if count < 1:
            _logger.error('Something wrong with recruit tankman default role!')
            self.__clearFilteredData()

    def __hasPredefinedNations(self):
        return bool(self.__predefinedNations)

    def __hasPredefinedTmanRoles(self):
        return bool(self.__predefinedTmanRoles)

    def __clearFilteredData(self):
        if self.__filteredNations is not None:
            self.__filteredNations.clear()
            self.__filteredNations = None
        if self.__filteredVehClasses is not None:
            self.__filteredVehClasses.clear()
            self.__filteredVehClasses = None
        if self.__filteredVehicles is not None:
            self.__filteredVehicles.clear()
            self.__filteredVehicles = None
        return

    def __sortNations(self, unsortedNatios):
        sortedNations = []
        for name in GUI_NATIONS:
            if name in unsortedNatios:
                sortedNations.append(name)

        return sortedNations
