# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/recruitWindow/RecruitParamsComponent.py
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.meta.RecruitParametersMeta import RecruitParametersMeta
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from items.tankmen import getSkillsConfig
from helpers.i18n import convert
from gui import GUI_NATIONS
import nations
from gui.Scaleform.locale.MENU import MENU
import Event
from skeletons.gui.shared import IItemsCache
DEFAULT_NATION = -1
DEFAULT_CLASS = ''
DEFAULT_VEHICLE = -1
DEFAULT_ROLE = ''

class RecruitParamsComponent(RecruitParametersMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(RecruitParamsComponent, self).__init__()
        self.onDataChange = Event.Event()
        self.__selectedNation = DEFAULT_NATION
        self.__selectedVehClass = DEFAULT_CLASS
        self.__selectedVehicle = DEFAULT_VEHICLE
        self.__selectedTmanRole = DEFAULT_ROLE
        self.__isRoleLocked = False

    def init(self):
        Waiting.show('updating')
        self.__setNationsData()
        self.__setVehicleClassesData()
        self.as_setVehicleDataS(self.__getSendingData([self.__getVehicleEmptyRow()], False, 0))
        if not self.__isRoleLocked:
            self.as_setTankmanRoleDataS(self.__getSendingData([self.__getTankmanRoleEmptyRow()], False, 0))
        Waiting.hide('updating')
        self.onDataChange(self.__selectedNation, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)

    def onNationChanged(self, nationID):
        if self.__selectedNation == nationID:
            return
        Waiting.show('updating')
        self.__selectedNation = nationID
        self.__setVehicleClassesData()
        self.as_setVehicleDataS(self.__getSendingData([self.__getVehicleEmptyRow()], False, 0))
        if not self.__isRoleLocked:
            self.as_setTankmanRoleDataS(self.__getSendingData([self.__getTankmanRoleEmptyRow()], False, 0))
        Waiting.hide('updating')
        self.onDataChange(self.__selectedNation, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)

    def onVehicleClassChanged(self, vehClass):
        if self.__selectedVehClass == vehClass:
            return
        Waiting.show('updating')
        self.__selectedVehClass = vehClass
        self.__setVehicleData()
        if not self.__isRoleLocked:
            self.as_setTankmanRoleDataS(self.__getSendingData([self.__getTankmanRoleEmptyRow()], False, 0))
        Waiting.hide('updating')
        self.onDataChange(self.__selectedNation, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)

    def onVehicleChanged(self, vehID):
        if self.__selectedVehicle == vehID:
            return
        Waiting.show('updating')
        self.__selectedVehicle = vehID
        self.__setTankmenData()
        Waiting.hide('updating')
        self.onDataChange(self.__selectedNation, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)

    def onTankmanRoleChanged(self, tManID):
        if self.__selectedTmanRole == tManID:
            return
        self.__selectedTmanRole = tManID
        self.onDataChange(self.__selectedNation, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)

    def _dispose(self):
        self.onDataChange.clear()
        super(RecruitParamsComponent, self)._dispose()

    def __setNationsData(self):
        vehsItems = self.itemsCache.items.getVehicles(self.__getNationsCriteria())
        data = []
        selectedNationIndex = 0
        counter = 0
        for name in GUI_NATIONS:
            nationIdx = nations.INDICES[name]
            vehiclesAvailable = len(vehsItems.filter(REQ_CRITERIA.NATIONS([nationIdx]))) > 0
            if name in nations.AVAILABLE_NAMES and vehiclesAvailable:
                if self.__selectedNation == DEFAULT_NATION:
                    self.__selectedNation = nationIdx
                data.append({'id': nationIdx,
                 'label': MENU.nations(name)})
                if nationIdx == self.__selectedNation:
                    selectedNationIndex = counter
                counter = counter + 1

        self.as_setNationsDataS(self.__getSendingData(data, len(data) > 1, selectedNationIndex))

    def __setVehicleClassesData(self):
        modulesAll = self.itemsCache.items.getVehicles(self.__getClassesCriteria(self.__selectedNation)).values()
        classes = []
        data = [self.__getVehicleClassEmptyRow()]
        modulesAll.sort()
        for module in modulesAll:
            if module.type in classes:
                continue
            classes.append(module.type)
            data.append({'id': module.type,
             'label': DIALOGS.recruitwindow_vehicleclassdropdown(module.type)})

        self.as_setVehicleClassDataS(self.__getSendingData(data, len(data) > 1, 0))

    def __setVehicleData(self):
        modulesAll = self.itemsCache.items.getVehicles(self.__getVehicleTypeCriteria(self.__selectedNation, self.__selectedVehClass)).values()
        data = [self.__getVehicleEmptyRow()]
        modulesAll.sort()
        selectedIndex = 0
        for i, module in enumerate(modulesAll):
            data.append({'id': module.innationID,
             'label': module.shortUserName})
            if module.innationID == self.__selectedVehicle:
                selectedIndex = i

        self.as_setVehicleDataS(self.__getSendingData(data, len(data) > 1, selectedIndex))

    def __setTankmenData(self):
        if not self.__isRoleLocked:
            modulesAll = self.itemsCache.items.getVehicles(self.__getRoleCriteria(self.__selectedNation, self.__selectedVehClass, self.__selectedVehicle)).values()
            roles = []
            data = [self.__getTankmanRoleEmptyRow()]
            modulesAll.sort()
            selectedIndex = 0
            counter = 0
            skillsConfig = getSkillsConfig()
            for module in modulesAll:
                for role in module.descriptor.type.crewRoles:
                    if role[0] in roles:
                        continue
                    roles.append(role[0])
                    data.append({'id': role[0],
                     'label': convert(skillsConfig.getSkill(role[0]).userString)})
                    if self.__selectedTmanRole == role[0]:
                        selectedIndex = counter
                    counter = counter + 1

            self.as_setTankmanRoleDataS(self.__getSendingData(data, len(data) > 1, selectedIndex))

    def setLockedRole(self, role):
        self.__isRoleLocked = True
        skillsConfig = getSkillsConfig()
        data = [self.__getTankmanRoleEmptyRow()]
        self.__selectedTmanRole = role
        data.append({'id': role,
         'label': convert(skillsConfig.getSkill(role).userString)})
        self.as_setTankmanRoleDataS(self.__getSendingData(data, False, 1))

    def __getSendingData(self, data, enabled, selectedIndex):
        return {'enabled': enabled,
         'selectedIndex': selectedIndex,
         'data': data}

    def __getNationsCriteria(self):
        return REQ_CRITERIA.UNLOCKED | ~REQ_CRITERIA.VEHICLE.OBSERVER

    def __getVehicleTypeCriteria(self, nationID, vclass):
        return self.__getClassesCriteria(nationID) | REQ_CRITERIA.VEHICLE.CLASSES([vclass])

    def __getClassesCriteria(self, nationID):
        return self.__getNationsCriteria() | REQ_CRITERIA.NATIONS([nationID])

    def __getRoleCriteria(self, nationID, vclass, typeID):
        return self.__getVehicleTypeCriteria(nationID, vclass) | REQ_CRITERIA.INNATION_IDS([typeID])

    def __getVehicleClassEmptyRow(self):
        return {'id': DEFAULT_CLASS,
         'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}

    def __getVehicleEmptyRow(self):
        return {'id': DEFAULT_VEHICLE,
         'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}

    def __getTankmanRoleEmptyRow(self):
        return {'id': DEFAULT_ROLE,
         'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}
