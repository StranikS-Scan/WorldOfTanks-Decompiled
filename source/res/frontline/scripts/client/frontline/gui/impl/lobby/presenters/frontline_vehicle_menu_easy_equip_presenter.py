# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/presenters/frontline_vehicle_menu_easy_equip_presenter.py
from __future__ import absolute_import
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel
from gui.prb_control.entities.base.listener import IPrbListener
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.base_menu_entry_sub_presenter import BaseMenuEntrySubPresenter

class FrontlineEasyEquipMenuEntrySubPresenter(BaseMenuEntrySubPresenter, IPrbListener):

    def _getState(self):
        return VehicleMenuModel.UNAVAILABLE

    def onNavigate(self):
        pass
