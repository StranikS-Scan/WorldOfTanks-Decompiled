# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCFittingPopover.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover import OptionalDeviceSelectPopover, _POPOVER_FIRST_TAB_IDX
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.locale.MENU import MENU
from bootcamp.BootcampGarage import g_bootcampGarage
from gui.Scaleform.framework import ViewTypes, g_entitiesFactories
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from bootcamp.Bootcamp import g_bootcamp

class BCFittingPopover(OptionalDeviceSelectPopover):
    _TABS = None

    def __init__(self, ctx=None):
        super(BCFittingPopover, self).__init__(ctx)
        self.__slotType = ''
        if 'data' in ctx:
            self.__slotType = ctx['data'].slotType
        self.__moduleInstalled = False
        self.setCurrentTab(_POPOVER_FIRST_TAB_IDX)
        self._TABS = None
        if self.__slotType == 'optionalDevice':
            self._TABS = [{'label': MENU.OPTIONALDEVICESELECTPOPOVER_TABS_SIMPLE,
              'id': 'simpleOptDevices'}]
        return

    def _populate(self):
        super(BCFittingPopover, self)._populate()
        if self.__slotType == 'optionalDevice':
            g_bootcampGarage.runViewAlias('bootcampFittingSelectPopoverMessage')

    def _dispose(self):
        super(BCFittingPopover, self)._dispose()
        if self.__slotType == 'optionalDevice':
            if self.__moduleInstalled:
                g_bootcampGarage.runCustomAction('showElementsLessonV_Step1')
            else:
                g_bootcampGarage.runViewAlias('hangar')

    def destroy(self):
        manager = self.app.containerManager
        container = manager.getContainer(ViewTypes.WINDOW)
        window = None
        if container:
            window = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.BOOTCAMP_MESSAGE_WINDOW})
        if window is None:
            super(BCFittingPopover, self).destroy()
        return

    def as_updateS(self, data):
        researchFreeLesson = g_bootcamp.getContextIntParameter('researchFreeLesson')
        if g_bootcamp.getLessonNum() >= researchFreeLesson and data['rendererName'] != FITTING_TYPES.GUN_TURRET_FITTING_ITEM_RENDERER:
            nationData = g_bootcampGarage.getNationData()
            optionalDeviceId = nationData['equipment']
            optionalDeviceValue = None
            deviceList = data['availableDevices']
            for device in deviceList:
                if device['id'] == optionalDeviceId:
                    optionalDeviceValue = device

            if optionalDeviceValue is not None:
                deviceList.remove(optionalDeviceValue)
                deviceList.insert(0, optionalDeviceValue)
            scrollCountOptionalDevices = g_bootcamp.getContextIntParameter('scrollCountOptionalDevices')
            del deviceList[scrollCountOptionalDevices:]
        super(BCFittingPopover, self).as_updateS(data)
        return

    def setVehicleModule(self, newId, oldId, isRemove):
        self.__moduleInstalled = not isRemove
        super(BCFittingPopover, self).setVehicleModule(newId, oldId, isRemove)
