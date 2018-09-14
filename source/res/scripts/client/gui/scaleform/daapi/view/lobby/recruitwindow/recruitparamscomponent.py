# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/recruitWindow/RecruitParamsComponent.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.meta.RecruitParametersMeta import RecruitParametersMeta
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from items.tankmen import getSkillsConfig
from helpers.i18n import convert
from gui import GUI_NATIONS
import nations
from gui.Scaleform.locale.MENU import MENU
import Event

class RecruitParamsComponent(RecruitParametersMeta):

    def __init__(self):
        super(RecruitParamsComponent, self).__init__()
        self.onDataChange = Event.Event()
        self.__selectedNation = None
        self.__selectedVehClass = None
        self.__selectedVehicle = None
        self.__selectedTmanRole = None
        return

    def setNationsData(self, nationID = None, enabled = True, showEmptyRow = True):
        self.__selectedNation = nationID
        vehsItems = g_itemsCache.items.getVehicles(self.__getNationsCriteria())
        data = [self.__getNationEmptyRow()] if showEmptyRow else []
        selectedNationIndex = 0
        counter = 0
        for name in GUI_NATIONS:
            nationIdx = nations.INDICES[name]
            vehiclesAvailable = len(vehsItems.filter(REQ_CRITERIA.NATIONS([nationIdx]))) > 0
            if name in nations.AVAILABLE_NAMES and vehiclesAvailable:
                if self.__selectedNation is None:
                    self.__selectedNation = nationIdx
                data.append({'id': nationIdx,
                 'label': MENU.nations(name)})
                if nationIdx == self.__selectedNation:
                    selectedNationIndex = counter
                counter = counter + 1

        self.as_setNationsDataS(self.__getSendingData(data, enabled, selectedNationIndex))
        self.onDataChange(self.__selectedNation, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)
        return

    def onNationChanged(self, nationID):
        self.changeNation(nationID)

    def changeNation(self, nationID):
        Waiting.show('updating')
        self.__selectedNation = nationID
        modulesAll = g_itemsCache.items.getVehicles(self.__getClassesCriteria(nationID)).values()
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
        self.as_setVehicleDataS(self.__getSendingData([self.__getVehicleEmptyRow()], False, 0))
        self.as_setTankmanRoleDataS(self.__getSendingData([self.__getTankmanRoleEmptyRow()], False, 0))
        Waiting.hide('updating')
        self.onDataChange(self.__selectedNation, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)

    def onVehicleClassChanged(self, vehClass):
        Waiting.show('updating')
        self.__selectedVehClass = vehClass
        modulesAll = g_itemsCache.items.getVehicles(self.__getVehicleTypeCriteria(self.__selectedNation, vehClass)).values()
        data = [self.__getVehicleEmptyRow()]
        modulesAll.sort()
        selectedIndex = 0
        for i, module in enumerate(modulesAll):
            data.append({'id': module.innationID,
             'label': module.shortUserName})
            if module.innationID == self.__selectedVehicle:
                selectedIndex = i

        self.as_setVehicleDataS(self.__getSendingData(data, len(data) > 1, selectedIndex))
        self.as_setTankmanRoleDataS(self.__getSendingData([self.__getTankmanRoleEmptyRow()], False, 0))
        Waiting.hide('updating')
        self.onDataChange(self.__selectedNation, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)

    def onVehicleChanged(self, vehID):
        Waiting.show('updating')
        self.__selectedVehicle = vehID
        modulesAll = g_itemsCache.items.getVehicles(self.__getRoleCriteria(self.__selectedNation, self.__selectedVehClass, self.__selectedVehicle)).values()
        roles = []
        data = [self.__getTankmanRoleEmptyRow()]
        modulesAll.sort()
        selectedIndex = 0
        counter = 0
        for module in modulesAll:
            for role in module.descriptor.type.crewRoles:
                if role[0] in roles:
                    continue
                roles.append(role[0])
                data.append({'id': role[0],
                 'label': convert(getSkillsConfig()[role[0]]['userString'])})
                if self.__selectedTmanRole == role[0]:
                    selectedIndex = counter
                counter = counter + 1

        self.as_setTankmanRoleDataS(self.__getSendingData(data, len(data) > 1, selectedIndex))
        Waiting.hide('updating')
        self.onDataChange(self.__selectedNation, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)

    def onTankmanRoleChanged(self, tManID):
        self.__selectedTmanRole = tManID
        self.onDataChange(self.__selectedNation, self.__selectedVehClass, self.__selectedVehicle, self.__selectedTmanRole)

    def _dispose(self):
        self.onDataChange.clear()
        super(RecruitParamsComponent, self)._dispose()

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

    def __getNationEmptyRow(self):
        return {'id': -1,
         'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}

    def __getVehicleClassEmptyRow(self):
        return {'id': None,
         'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}

    def __getVehicleEmptyRow(self):
        return {'id': None,
         'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}

    def __getTankmanRoleEmptyRow(self):
        return {'id': None,
         'label': DIALOGS.RECRUITWINDOW_MENUEMPTYROW}
