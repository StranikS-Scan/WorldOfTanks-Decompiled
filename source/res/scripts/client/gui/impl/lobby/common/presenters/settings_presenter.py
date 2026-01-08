# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/presenters/settings_presenter.py
from __future__ import absolute_import
from inspect import getmembers
from past.builtins import long
import logging
import typing
from account_helpers.AccountSettings import AccountSettings
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.settings_model import SettingsModel
from gui.impl.gui_decorators import args2params
from gui.impl.pub.view_component import ViewComponent
if typing.TYPE_CHECKING:
    from typing import Type, Dict, Any, Callable, TypedDict
    Accessor = TypedDict('Accessor', {'value': Any,
     'getter': Callable,
     'setter': Callable})
_logger = logging.getLogger(__name__)

class SettingsPresenter(ViewComponent[SettingsModel]):

    def __init__(self, modelCls, accountSettingsKey, readOnly=False):
        super(SettingsPresenter, self).__init__(model=modelCls)
        self.__settingsKey = accountSettingsKey
        self.__readOnly = readOnly
        self.__settingsMap = {}
        submodels = {name:value for name, value in getmembers(self.viewModel) if isinstance(value, ViewModel)}
        validated = True
        settingsMap = {}
        for section, settings in AccountSettings.getSettings(accountSettingsKey).items():
            if not validated:
                break
            if section not in submodels:
                _logger.error('Settings section "%s" is not defined in %s!', section, self.viewModel)
                validated = False
                break
            settingsMap[section] = {}
            for key, value in settings.items():
                submodel = submodels[section]
                capitalizedName = '%c%s' % (key[0].upper(), key[1:])
                getter = getattr(submodel, 'get%s' % capitalizedName, None)
                setter = getattr(submodel, 'set%s' % capitalizedName, None)
                if getter is None or setter is None:
                    _logger.error('Setting property "%s" is not defined in %s', key, submodel)
                    validated = False
                    break
                valueT = type(value)
                prop = getter()
                propT = type(prop)
                if propT is long:
                    propT = int
                if valueT is not propT:
                    _logger.error('Setting property "%s" type mismatch %s != %s', key, valueT, propT)
                    validated = False
                    break
                settingsMap[section][key] = {'value': value,
                 'getter': getter,
                 'setter': setter}

        if not validated:
            _logger.error('Settings validation failed, check %s entry in AccountSettings and the %s model definition', self.__settingsKey, self.viewModel.__class__.__name__)
            return
        else:
            self.__settingsMap = settingsMap
            return

    @property
    def viewModel(self):
        return super(SettingsPresenter, self).getViewModel()

    def _finalize(self):
        self.__settingsMap.clear()
        super(SettingsPresenter, self)._finalize()

    def _getEvents(self):
        return ((AccountSettings.onSettingsChanging, self.__onAccountSettingsUpdated), (self.viewModel.onUpdateSetting, self.__onUpdateSetting))

    def _onLoading(self, *args, **kwargs):
        super(SettingsPresenter, self)._onLoading(*args, **kwargs)
        self.viewModel.setReadOnly(self.__readOnly)
        self.__fillModel()

    def __fillModel(self):
        for _, settings in self.__settingsMap.items():
            for _, accessor in settings.items():
                accessor['setter'](accessor['value'])

    __Any = lambda v: v

    @args2params(str, str, __Any)
    def __onUpdateSetting(self, section, key, value):
        _logger.debug('Updating setting %s/%s: %s', section, key, value)
        if section not in self.__settingsMap or key not in self.__settingsMap[section]:
            _logger.error('Attempting to update unknown setting %s/%s', section, key)
            return
        if self.__readOnly:
            _logger.error('Attempting to update a read-only setting %s/%s', section, key)
            return
        self.__settingsMap[section][key]['value'] = value
        AccountSettings.setSettings(self.__settingsKey, {section:{key:accessor['value'] for key, accessor in settings.items()} for section, settings in self.__settingsMap.items()})

    def __onAccountSettingsUpdated(self, settingsKey, _):
        if settingsKey != self.__settingsKey:
            return
        for section, settings in AccountSettings.getSettings(settingsKey).items():
            for key, value in settings.items():
                self.__settingsMap[section][key]['value'] = value

        self.__fillModel()
