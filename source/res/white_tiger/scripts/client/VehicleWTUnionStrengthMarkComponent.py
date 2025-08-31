# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/VehicleWTUnionStrengthMarkComponent.py
from script_component.DynamicScriptComponent import DynamicScriptComponent
from white_tiger.gui.gui_constants import FEEDBACK_EVENT_ID

class VehicleWTUnionStrengthMarkComponent(DynamicScriptComponent):

    def __init__(self):
        super(VehicleWTUnionStrengthMarkComponent, self).__init__()
        self._guiFeedback = self.entity.guiSessionProvider.shared.feedback

    def onDestroy(self):
        self.__updateMarker(False)

    def set_numberOfMarks(self, prev):
        if self.numberOfMarks != prev:
            isShow = True if self.numberOfMarks > 0 else False
            self.__updateMarker(isShow)

    def __updateMarker(self, isShow=True):
        numberOfMarks = self.numberOfMarks if isShow else 0
        self._guiFeedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.WT_VEHICLE_UNION_STRENGTH_MARK, self.entity.id, {'isShown': isShow,
         'numberOfMarks': numberOfMarks})
