# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/sub_views/deal_base_setup.py
from BWUtil import AsyncReturn
from async import async, await_callback, await
from gui.impl.lobby.tank_setup.configurations.base import BaseDealPanel
from gui.impl.lobby.tank_setup.sub_views.base_setup import BaseSetupSubView
from gui.impl.lobby.tank_setup.tank_setup_sounds import playSound, TankSetupSoundEvents

class DealBaseSetupSubView(BaseSetupSubView):
    __slots__ = ()

    def update(self, fullUpdate=False):
        super(DealBaseSetupSubView, self).update(fullUpdate)
        self._updateDealPanel()

    def updateSlots(self, slotID, fullUpdate=True, updateData=True):
        super(DealBaseSetupSubView, self).updateSlots(slotID, fullUpdate, updateData)
        self._updateDealPanel()

    @async
    def canQuit(self, skipApplyAutoRenewal=None):
        result = True
        if self._asyncActionLock.isLocked:
            raise AsyncReturn(False)
        elif self._interactor.hasChanged():
            dialogResult = yield await(self._asyncActionLock.tryAsyncCommand(self._interactor.showExitConfirmDialog))
            if dialogResult is None or dialogResult.busy:
                raise AsyncReturn(False)
            isOK, data = dialogResult.result
            if isOK:
                yield await_callback(self._onConfirm)(skipDialog=True)
                playSound(TankSetupSoundEvents.ACCEPT)
            elif data.get('rollBack', False):
                self._interactor.revert()
            else:
                result = False
        if result:
            yield await_callback(self._interactor.applyQuit)(skipApplyAutoRenewal=skipApplyAutoRenewal)
        raise AsyncReturn(result)
        return

    def _addListeners(self):
        super(DealBaseSetupSubView, self)._addListeners()
        self._viewModel.onDealConfirmed += self._onDealConfirmed
        self._viewModel.onDealCancelled += self._onDealCancelled
        self._viewModel.onAutoRenewalChanged += self._onAutoRenewalChanged

    def _removeListeners(self):
        super(DealBaseSetupSubView, self)._removeListeners()
        self._viewModel.onDealConfirmed -= self._onDealConfirmed
        self._viewModel.onDealCancelled -= self._onDealCancelled
        self._viewModel.onAutoRenewalChanged -= self._onAutoRenewalChanged

    def _getDealPanel(self):
        return BaseDealPanel

    def _updateDealPanel(self):
        if self._viewModel is None:
            return
        else:
            currentItems = self._interactor.getChangedList()
            vehicle = self._interactor.getItem()
            self._getDealPanel().updateDealPanelPrice(vehicle, currentItems, self._viewModel.dealPanel)
            self._getDealPanel().updateAutoRenewalState(self._interactor, self._viewModel.dealPanel)
            self._viewModel.dealPanel.setCanAccept(self._interactor.hasChanged())
            return

    @async
    def _onDealConfirmed(self, _=None):
        result = yield await(self._asyncActionLock.tryAsyncCommandWithCallback(self._onConfirm))
        if result:
            playSound(TankSetupSoundEvents.ACCEPT)
            yield await_callback(self._interactor.applyAutoRenewal)()
            self._interactor.onAcceptComplete()
        self._updateDealPanel()

    def _onDealCancelled(self, _=None):
        self._interactor.revert()
        self.update()

    def _onAutoRenewalChanged(self, args):
        newValue = args.get('value')
        self._interactor.getAutoRenewal().setLocalValue(newValue)
        self._getDealPanel().updateAutoRenewalState(self._interactor, self._viewModel.dealPanel)
