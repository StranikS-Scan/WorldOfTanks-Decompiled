# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/lobby/vehicle_preview/vehicle_preview_dp.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview_dp import DefaultVehPreviewDataProvider
from gui.shared.gui_items.items_actions import factory

class BCVehPreviewDataProvider(DefaultVehPreviewDataProvider):

    def getBuyType(self, vehicle):
        return factory.BUY_VEHICLE if vehicle.isUnlocked else factory.BC_UNLOCK_ITEM

    def buyAction(self, actionType, vehicleCD, skipConfirm, level=-1):
        if actionType == factory.BC_UNLOCK_ITEM:
            unlockProps = g_techTreeDP.getUnlockProps(vehicleCD, level)
            factory.doAction(factory.BC_UNLOCK_ITEM, vehicleCD, unlockProps, skipConfirm=skipConfirm)
        else:
            factory.doAction(factory.BUY_VEHICLE, vehicleCD, False, None, VIEW_ALIAS.VEHICLE_PREVIEW, skipConfirm=skipConfirm)
        return
