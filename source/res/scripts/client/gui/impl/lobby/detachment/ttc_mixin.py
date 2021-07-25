# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/ttc_mixin.py
from gui.shared import g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import DetachmentViewEvent
from items.components.detachment_constants import NO_DETACHMENT_ID

class TTCMixin(object):

    def __init__(self, *args, **kwargs):
        super(TTCMixin, self).__init__(*args, **kwargs)
        self.__isVisible = True
        self.__previousDisplayProps = None
        return

    def _addListeners(self):
        super(TTCMixin, self)._addListeners()
        self._ttcModel.updateTTCPosition += self._updateTTCDisplayProps
        g_eventBus.addListener(DetachmentViewEvent.ESCAPE, self._escape, EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        super(TTCMixin, self)._removeListeners()
        self._ttcModel.updateTTCPosition -= self._updateTTCDisplayProps
        g_eventBus.removeListener(DetachmentViewEvent.ESCAPE, self._escape, EVENT_BUS_SCOPE.LOBBY)

    def _setTTCVisibility(self, isVisible):
        if self.__isVisible == isVisible:
            return
        self.__isVisible = isVisible
        if self.__previousDisplayProps:
            self._updateTTCDisplayProps(self.__previousDisplayProps)

    @property
    def _ttcModel(self):
        return self.viewModel.ttcModel

    def _updateTTCDisplayProps(self, args=None):
        self.__previousDisplayProps = args
        g_eventBus.handleEvent(DetachmentViewEvent(DetachmentViewEvent.UPDATE_TTC_DISPLAY_PROPS, ctx=dict(args, isVisible=self.__isVisible)), EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def _updateTTCVehicle(vehicleItem):
        g_eventBus.handleEvent(DetachmentViewEvent(DetachmentViewEvent.UPDATE_TTC_VEHICLE, {'vehicleItem': vehicleItem}), EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def _updateTTCCurrentDetachment(detachmentID=NO_DETACHMENT_ID):
        g_eventBus.handleEvent(DetachmentViewEvent(DetachmentViewEvent.UPDATE_TTC_CURRENT_DETACHMENT, {'detachmentID': detachmentID}), EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def _updateTTCBonusDetachment(detachmentID):
        g_eventBus.handleEvent(DetachmentViewEvent(DetachmentViewEvent.UPDATE_TTC_BONUS_DETACHMENT, {'detachmentID': detachmentID}), EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def _updateTTCPerks(bonusPerks=None, comparableInstructor=False):
        g_eventBus.handleEvent(DetachmentViewEvent(DetachmentViewEvent.UPDATE_TTC_PERKS, {'bonusPerks': bonusPerks or {},
         'comparableInstructor': comparableInstructor}), EVENT_BUS_SCOPE.LOBBY)

    def _escape(self, event):
        self._onEscape()
