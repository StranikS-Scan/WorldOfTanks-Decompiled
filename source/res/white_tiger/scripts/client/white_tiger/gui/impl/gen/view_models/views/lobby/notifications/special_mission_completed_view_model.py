# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/notifications/special_mission_completed_view_model.py
from gui.impl.gen.view_models.common.notification_base_model import NotificationBaseModel

class SpecialMissionCompletedViewModel(NotificationBaseModel):
    __slots__ = ('onClose', 'onGoToBadge')

    def __init__(self, properties=1, commands=2):
        super(SpecialMissionCompletedViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(SpecialMissionCompletedViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
        self.onGoToBadge = self._addCommand('onGoToBadge')
