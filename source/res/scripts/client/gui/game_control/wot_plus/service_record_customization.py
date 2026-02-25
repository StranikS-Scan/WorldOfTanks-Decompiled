# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus/service_record_customization.py
import typing
import BigWorld
from gui.shared.gui_items.processors import Processor
from gui.shared.gui_items.processors.plugins import SyncValidator, makeSuccess, makeError
from helpers import dependency
from skeletons.gui.game_control import IWotPlusController
if typing.TYPE_CHECKING:
    from typing import Tuple, Optional, Any, Generator
_SERVICE_RECORD_ASSETS_MAP = {'background': ('default', 'legendary', 'golden', 'smashing', 'fiery', 'retro'),
 'ribbon': ('red', 'purple', 'gold', 'green', 'silver', 'black')}

class _HasWotPlusValidator(SyncValidator):
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)

    def _validate(self):
        return makeSuccess() if self._wotPlusCtrl.hasSubscription() else makeError('Player has no WotPlus subscription')


class _IsSRCustomizationEnabledValidator(SyncValidator):
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)

    def _validate(self):
        return makeSuccess() if self._wotPlusCtrl.getSettingsStorage().isServiceRecordCustomizationAvailable() else makeError('WotPlus service record customization is disabled')


class _RangeValidator(SyncValidator):

    def __init__(self, optionsList, option, isEnabled=True):
        super(_RangeValidator, self).__init__(isEnabled)
        self._optionsList = optionsList
        self._option = option

    def _validate(self):
        return makeError('Option index is out of range') if self._option is None or self._option < 0 or self._option >= len(self._optionsList) else makeSuccess()


class ServiceRecordProcessor(Processor):

    def __init__(self, background, ribbon):
        self._background = background
        self._ribbon = ribbon
        plugins = [_HasWotPlusValidator(),
         _IsSRCustomizationEnabledValidator(),
         _RangeValidator(_SERVICE_RECORD_ASSETS_MAP['ribbon'], ribbon),
         _RangeValidator(_SERVICE_RECORD_ASSETS_MAP['background'], background)]
        super(ServiceRecordProcessor, self).__init__(plugins)

    def _request(self, callback):
        BigWorld.player().setServiceRecordCustomizations(self._ribbon, self._background, lambda code, errStr: self._response(code, callback, errStr=errStr))


def getValidatedServiceRecordBackground(index):
    return _getServiceRecord(_SERVICE_RECORD_ASSETS_MAP['background'], index)


def getValidatedServiceRecordRibbon(index):
    return _getServiceRecord(_SERVICE_RECORD_ASSETS_MAP['ribbon'], index)


def _getServiceRecord(optionsList, index):
    if index is None or index < 0 or index >= len(optionsList):
        index = 0
    return (index, optionsList[index])


def getServiceRecordBackgroundOptions():
    for idx, background in enumerate(_SERVICE_RECORD_ASSETS_MAP['background']):
        yield (idx, background)


def getServiceRecordRibbonOptions():
    for idx, ribbon in enumerate(_SERVICE_RECORD_ASSETS_MAP['ribbon']):
        yield (idx, ribbon)
