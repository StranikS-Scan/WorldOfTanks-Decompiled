# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/guided_missile_widget.py
import BigWorld
import CGF
from aih_constants import CTRL_MODE_NAME
from AvatarInputHandler import aih_global_binding
from GuidedMissileReplicableComponent import GuidedMissileReplicableComponent
from portal.gui.Scaleform.daapi.view.meta.PortalGuidedMissileWidgetMeta import PortalGuidedMissileWidgetMeta

class GuidedMissileWidget(PortalGuidedMissileWidgetMeta):

    def _populate(self):
        super(GuidedMissileWidget, self)._populate()
        aih_global_binding.subscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self.__onAvatarCtrlModeChanged)

    def _dispose(self):
        aih_global_binding.unsubscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self.__onAvatarCtrlModeChanged)
        super(GuidedMissileWidget, self)._dispose()

    def __update(self):
        flightTime = self.__getFlightTime()
        self.as_updateTimeS(flightTime)

    def __getFlightTime(self):
        flightTime = 0
        avatar = BigWorld.player()
        query = CGF.Query(avatar.spaceID, (GuidedMissileReplicableComponent,))
        for guidedMissile in query:
            if guidedMissile.replicableAvatarId == avatar.id:
                flightTime = guidedMissile.flightFinishTime - BigWorld.serverTime()
                break

        return max(int(flightTime), 0)

    def __onAvatarCtrlModeChanged(self, ctrlMode):
        if ctrlMode == CTRL_MODE_NAME.ATGM:
            self.__update()
