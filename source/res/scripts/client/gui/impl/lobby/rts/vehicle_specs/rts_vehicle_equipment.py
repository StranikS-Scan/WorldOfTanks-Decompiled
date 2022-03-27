# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/vehicle_specs/rts_vehicle_equipment.py
from gui.impl.gen.resources import R
from gui.shared.gui_items.Vehicle import Vehicle
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_vehicle_specs_view_model import RosterVehicleSpecsViewModel
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_vehicle_equipment_view_model import RosterVehicleEquipmentViewModel
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_vehicle_ammunition_view_model import RosterVehicleAmmunitionViewModel
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_vehicle_crew_member_view_model import RosterVehicleCrewMemberViewModel, CrewMemberType
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_vehicle_crew_member_skill_view_model import RosterVehicleCrewMemberSkillViewModel, CrewMemberSkill

class RtsVehicleEquipmentBase(object):

    def __init__(self, vehicle):
        self._vehicle = vehicle

    @property
    def entries(self):
        raise NotImplementedError

    def targetProperty(self, model):
        raise NotImplementedError

    def _createItem(self, item):
        raise NotImplementedError

    def _setItems(self, model):
        items = [ item for item in self.entries if item ]
        if not items:
            return
        with model.transaction() as vm:
            itemArray = self.targetProperty(vm)
            itemArray.clear()
            itemArray.reserve(len(items))
            for item in items:
                itemArray.addViewModel(self._createItem(item))

        itemArray.invalidate()

    def updateModel(self, model):
        with model.transaction() as vm:
            self._setItems(vm)


class RtsVehicleEquipment(RtsVehicleEquipmentBase):

    @property
    def entries(self):
        return self._vehicle.optDevices.installed

    def targetProperty(self, model):
        return model.getEquipment()

    def _createItem(self, item):
        itemModel = RosterVehicleEquipmentViewModel()
        image = R.images.gui.maps.icons.artefact.dyn(item.descriptor.iconName)()
        itemModel.setImage(image)
        itemModel.setIntCd(item.intCD)
        return itemModel


class RtsVehicleConsumables(RtsVehicleEquipment):

    @property
    def entries(self):
        return self._vehicle.consumables.installed

    def targetProperty(self, model):
        return model.getConsumables()


class RtsVehicleAmmo(RtsVehicleEquipmentBase):

    @property
    def entries(self):
        return self._vehicle.shells.installed

    def targetProperty(self, model):
        return model.getAmmunition()

    def _createItem(self, item):
        itemModel = RosterVehicleAmmunitionViewModel()
        image = R.images.gui.maps.icons.shell.small.dyn(item.descriptor.iconName)()
        itemModel.setImage(image)
        itemModel.setIntCd(item.intCD)
        itemModel.setCount(item.count)
        return itemModel


class RtsVehicleCrew(RtsVehicleEquipmentBase):

    @property
    def entries(self):
        return [ crewMemberEntry[1] for crewMemberEntry in self._vehicle.crew if crewMemberEntry ]

    def targetProperty(self, model):
        return model.getCrew()

    def _createItem(self, item):
        crewMemberModel = RosterVehicleCrewMemberViewModel()
        crewMemberModel.setType(CrewMemberType(item.role))
        skillsArray = crewMemberModel.getSkills()
        skillsArray.clear()
        skillsArray.reserve(len(item.skills))
        for skill in item.skills:
            skillModel = RosterVehicleCrewMemberSkillViewModel()
            skillModel.setName(CrewMemberSkill(skill.name))
            skillsArray.addViewModel(skillModel)

        return crewMemberModel


def updateVehicleEquipment(model, vehicle):
    updaters = (RtsVehicleEquipment,
     RtsVehicleConsumables,
     RtsVehicleAmmo,
     RtsVehicleCrew)
    for updater in updaters:
        updater(vehicle).updateModel(model)

    return model
