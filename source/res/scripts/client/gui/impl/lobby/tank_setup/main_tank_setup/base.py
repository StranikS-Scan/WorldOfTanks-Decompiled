# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/main_tank_setup/base.py
import logging
from BWUtil import AsyncReturn
from async import async, await, await_callback
from gui.impl.common.base_sub_model_view import BaseSubModelView
from gui.impl.lobby.tank_setup.tank_setup_sounds import playSectionSelectSound
_logger = logging.getLogger(__name__)

class MainTankSetupView(BaseSubModelView):
    __slots__ = ('_subViews', '_builder', '__isLocked')

    def __init__(self, viewModel, builder=None):
        super(MainTankSetupView, self).__init__(viewModel)
        self._builder = builder
        self._subViews = {}
        self.__isLocked = False

    def setLocked(self, value):
        self.__isLocked = value

    def currentVehicleUpdated(self, vehicle):
        for name, subView in self._subViews.iteritems():
            subView.getInteractor().updateFrom(vehicle, name == self.getSelectedSetup())

    def resetVehicle(self, interactingItem):
        for subView in self._subViews.values():
            subView.getInteractor().setItem(interactingItem)

    def onLoading(self, selectedSection='', selectedSlot=None):
        self._viewModel.setSelectedSetup(selectedSection)
        self._subViews = self._builder.configureBuild(self._viewModel)
        if selectedSection:
            if selectedSection in self._subViews:
                self._subViews[selectedSection].onLoading(int(selectedSlot))
            else:
                _logger.error('There is not selectedSection=[%s] in subViews=[%s]', selectedSection, self._subViews)

    def initialize(self, *args, **kwargs):
        super(MainTankSetupView, self).initialize(*args, **kwargs)
        for subView in self._subViews.itervalues():
            subView.initialize()

    def finalize(self):
        for subView in self._subViews.itervalues():
            subView.finalize()

        self._subViews.clear()
        self._builder = None
        super(MainTankSetupView, self).finalize()
        return

    def getSelectedSetup(self):
        return self._viewModel.getSelectedSetup()

    def getCurrentSubView(self):
        selectedSetup = self._viewModel.getSelectedSetup()
        return self.getSubView(selectedSetup)

    def getSubView(self, sectionName):
        return self._subViews[sectionName] if sectionName in self._subViews else None

    def update(self, fullUpdate=False):
        if self.__isLocked:
            return
        else:
            currentSubView = self.getCurrentSubView()
            if currentSubView is not None:
                currentSubView.update(fullUpdate=fullUpdate)
            return

    @async
    def canQuit(self, skipApplyAutoRenewal=None):
        selectedView = self.getCurrentSubView()
        if selectedView is not None:
            quitResult = yield await(selectedView.canQuit(skipApplyAutoRenewal=skipApplyAutoRenewal))
        else:
            quitResult = True
        raise AsyncReturn(quitResult)
        return

    @async
    def switch(self, setupName, slotID):
        if setupName not in self._subViews:
            _logger.error('MainTankSetupView doesnt have sub view by name: %s', setupName)
            raise AsyncReturn(False)
        selectedSetup = self._viewModel.getSelectedSetup()
        if selectedSetup == setupName:
            self._subViews[setupName].updateSlots(slotID, fullUpdate=False)
            raise AsyncReturn(True)
        if selectedSetup:
            quitResult = yield await(self._subViews[selectedSetup].canQuit())
        else:
            quitResult = True
        if quitResult:
            yield self._doSwitch(setupName, slotID)
        raise AsyncReturn(quitResult)

    @async
    def _doSwitch(self, setupName, slotID):
        subView = self._subViews[setupName]
        if not subView.isLoaded():
            subView.onLoading(slotID)
        else:
            subView.updateSlots(slotID)
        self._viewModel.setSelectedSetup(setupName)
        playSectionSelectSound()
        yield await_callback(lambda callback: callback())()
        raise AsyncReturn(None)
        return
