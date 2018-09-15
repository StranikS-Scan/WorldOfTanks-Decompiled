# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_box_popover.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.ny.ny_common import NO_SETTING_BOX_ID
from gui.Scaleform.daapi.view.meta.NYBoxPopoverMeta import NYBoxPopoverMeta
from gui.server_events.events_dispatcher import showMissions
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from helpers import dependency
from items.new_year_types import NATIONAL_SETTINGS
from skeletons.new_year import INewYearController, ICustomizableObjectsManager

class NYBoxPopover(NYBoxPopoverMeta):
    _newYearController = dependency.descriptor(INewYearController)
    _customizableObjMgr = dependency.descriptor(ICustomizableObjectsManager)

    def __init__(self, ctx=None):
        super(NYBoxPopover, self).__init__(ctx)
        self.__backAlias = ctx.get('previewAlias', VIEW_ALIAS.LOBBY_HANGAR)

    def _populate(self):
        super(NYBoxPopover, self)._populate()
        self.__updeateData()
        self._newYearController.boxStorage.onCountChanged += self.__onCountChanged
        self._newYearController.onStateChanged += self.__onNyStateChanged

    def _dispose(self):
        self._newYearController.onStateChanged -= self.__onNyStateChanged
        self._newYearController.boxStorage.onCountChanged -= self.__onCountChanged
        super(NYBoxPopover, self)._dispose()

    def toShop(self):
        self.fireEvent(events.OpenLinkEvent(events.OpenLinkEvent.NY18_SHOP))

    def boxOpen(self, setting):
        setting = setting if setting in NATIONAL_SETTINGS else None
        if self._newYearController.boxStorage.canOpen(self._newYearController.boxStorage.getItemIDBySetting(setting)):
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_NY_MISSIONS_REWARD_RECEIPT, name=VIEW_ALIAS.LOBBY_NY_MISSIONS_REWARD_RECEIPT, ctx={'nySettingID': setting,
             'previewAlias': self.__backAlias}), EVENT_BUS_SCOPE.LOBBY)
        return

    def toEarn(self):
        self._customizableObjMgr.switchTo(None, showMissions)
        return

    def __onNyStateChanged(self, _):
        if not self._newYearController.isAvailable():
            self.destroy()

    def __onCountChanged(self, *args):
        self.__updeateData()

    def __updeateData(self):
        boxes = []
        lastSetting = None
        ordered_by_setting = self._newYearController.boxStorage.getOrderedBoxes()
        for descr, count in ordered_by_setting:
            if descr.setting is not None:
                setting_id = descr.setting
            else:
                setting_id = NO_SETTING_BOX_ID
            if lastSetting == setting_id:
                boxes[len(boxes) - 1]['count'] += count
            else:
                boxes.append({'id': setting_id,
                 'count': count})
            lastSetting = setting_id

        self.as_setDataS(boxes)
        return
