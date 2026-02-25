# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/presenters/fun_random_vehicle_menu_easy_equip_presenter.py
from __future__ import absolute_import
from gui.prb_control.entities.base.listener import IPrbListener
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.base_menu_entry_sub_presenter import BaseMenuEntrySubPresenter
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel

class FunRandomEasyEquipMenuEntrySubPresenter(BaseMenuEntrySubPresenter, IPrbListener):

    def _getState(self):
        return VehicleMenuModel.UNAVAILABLE

    def onNavigate(self):
        pass
