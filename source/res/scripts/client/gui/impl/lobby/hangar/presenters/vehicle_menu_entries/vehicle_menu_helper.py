# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_menu_entries/vehicle_menu_helper.py
from __future__ import absolute_import
import typing
from gui.impl.gen import R
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.about_vehicle_entry_sub_presenter import AboutVehicleEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.armor_inspector_entry_sub_presenter import ArmorInspectorEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.compare_entry_sub_presenter import CompareEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.crew_auto_return_entry_sub_presenter import CrewAutoReturnEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.crew_back_entry_sub_presenter import CrewBackEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.crew_out_entry_sub_presenter import CrewOutEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.crew_retrain_entry_sub_presenter import CrewRetrainEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.customization_entry_sub_presenter import CustomizationEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.easy_equip_entry_sub_presenter import EasyEquipEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.field_modification_entry_sub_presenter import FieldModificationEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.nation_change_entry_sub_presenter import NationChangeEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.quick_training_entry_sub_presenter import QuickTrainingEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.repairs_entry_sub_presenter import RepairsEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.research_entry_sub_presenter import ResearchEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.vehicle_skill_tree_entry_sub_presenter import VehicleSkillTreeEntrySubPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.wot_plus_entry_sub_presenter import WotPlusEntrySubPresenter

class IHangarVehicleMenuHelper(object):

    @classmethod
    def getMenuEntries(cls):
        raise NotImplementedError


class DefaultHangarVehicleMenuHelper(IHangarVehicleMenuHelper):

    @classmethod
    def getMenuEntries(cls):
        vehicleMenu = R.aliases.vehicle_menu.default
        return {vehicleMenu.Customization(): CustomizationEntrySubPresenter,
         vehicleMenu.CrewAutoReturn(): CrewAutoReturnEntrySubPresenter,
         vehicleMenu.CrewRetrain(): CrewRetrainEntrySubPresenter,
         vehicleMenu.QuickTraining(): QuickTrainingEntrySubPresenter,
         vehicleMenu.CrewOut(): CrewOutEntrySubPresenter,
         vehicleMenu.CrewBack(): CrewBackEntrySubPresenter,
         vehicleMenu.EasyEquip(): EasyEquipEntrySubPresenter,
         vehicleMenu.ArmorInspector(): ArmorInspectorEntrySubPresenter,
         vehicleMenu.FieldModification(): FieldModificationEntrySubPresenter,
         vehicleMenu.NationChange(): NationChangeEntrySubPresenter,
         vehicleMenu.Research(): ResearchEntrySubPresenter,
         vehicleMenu.AboutVehicle(): AboutVehicleEntrySubPresenter,
         vehicleMenu.Compare(): CompareEntrySubPresenter,
         vehicleMenu.Repairs(): RepairsEntrySubPresenter,
         vehicleMenu.VehSkillTree(): VehicleSkillTreeEntrySubPresenter,
         vehicleMenu.ProBoost(): WotPlusEntrySubPresenter}
