# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/builders.py
import importlib
import logging
from typing import Any
from gui.Scaleform.daapi.settings.config import ADVANCED_COMPLEX_TOOLTIPS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.gui_items.artefacts import OptionalDevice
from gui.shared.tooltips import complex_formatters
from gui.shared.tooltips import contexts, advanced
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
DISABLED_ITEMS_ID = 12793

class TooltipBuilder(object):
    __slots__ = ('_tooltipType', '_linkage', '_provider')

    def __init__(self, tooltipType, linkage):
        super(TooltipBuilder, self).__init__()
        self._tooltipType = tooltipType
        self._linkage = linkage
        self._provider = None
        return

    @property
    def tooltipType(self):
        return self._tooltipType

    @property
    def linkage(self):
        return self._linkage

    @property
    def provider(self):
        return self._provider

    def build(self, stateType, advanced_, *args, **kwargs):
        raise NotImplementedError

    def supportAdvanced(self, tooltipType, *args):
        return False


class SimpleBuilder(TooltipBuilder):
    __slots__ = ()

    def build(self, stateType, advanced_, *args, **kwargs):
        return (self._provider, args, self._linkage)


class AdvancedBuilder(TooltipBuilder):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def _getDisableAnimFlag(self):
        return self.__settingsCore.serverSettings.getDisableAnimTooltipFlag() if self.__settingsCore.serverSettings.settingsCache.settings.isSynced() else True

    def _setDisableAnimFlag(self):
        if self.__settingsCore.serverSettings.settingsCache.settings.isSynced():
            self.__settingsCore.serverSettings.setDisableAnimTooltipFlag()


class DataBuilder(SimpleBuilder):
    __slots__ = ('_provider',)

    def __init__(self, tooltipType, linkage, provider):
        super(DataBuilder, self).__init__(tooltipType, linkage)
        self._provider = provider
        self._provider.calledBy = tooltipType

    def build(self, formatType, advanced_, *args, **kwargs):
        data = self._buildData(advanced_, *args, **kwargs)
        return (self._provider, data, self._linkage)

    def _buildData(self, advanced_, *args, **kwargs):
        return self._provider.buildToolTip(*args, **kwargs)


class TooltipWindowBuilder(DataBuilder):

    def build(self, formatType, advanced_, *args, **kwargs):
        self._buildData(advanced_, *args, **kwargs)
        return self._provider


class AdvancedTooltipWindowBuilder(AdvancedBuilder):
    __slots__ = ('_adProvider', '_condition', '_provider')

    def __init__(self, tooltipType, linkage, provider, adProvider, condition=None):
        super(AdvancedTooltipWindowBuilder, self).__init__(tooltipType, linkage)
        self._adProvider = adProvider
        self._condition = condition
        self._provider = provider

    def build(self, formatType, advanced_, *args, **kwargs):
        supportAdvanced = self.supportAdvanced(self._tooltipType, *args)
        return self._adProvider if advanced_ and supportAdvanced else self._provider

    def supportAdvanced(self, tooltipType, *args):
        return self._condition(*args) if self._condition is not None else True


class AdvancedDataBuilder(AdvancedBuilder):
    __slots__ = ('_provider', '_adProvider', '_condition')

    def __init__(self, tooltipType, linkage, provider, adProvider, condition=None):
        super(AdvancedDataBuilder, self).__init__(tooltipType, linkage)
        self._provider = provider
        self._adProvider = adProvider
        self._condition = condition

    def build(self, formatType, advanced_, *args, **kwargs):
        data = self._buildData(advanced_, *args, **kwargs)
        return (self._provider, data, self._linkage)

    def supportAdvanced(self, tooltipType, *args):
        return self._condition(*args) if self._condition is not None else True

    def _buildData(self, advanced_, *args, **kwargs):
        disableAnim = self._getDisableAnimFlag()
        supportAdvanced = self.supportAdvanced(self._tooltipType, *args)
        if advanced_ and supportAdvanced:
            data = self._adProvider.buildToolTip(*args)
            if not disableAnim:
                self._setDisableAnimFlag()
        else:
            data = self._provider.buildToolTip(*args)
            item = self._provider.item
            disabledForWheeled = False
            if item is not None:
                if isinstance(item, OptionalDevice):
                    disabledForWheeled = item.intCD == DISABLED_ITEMS_ID
            if supportAdvanced and not disabledForWheeled:
                self._provider.addAdvancedBlock(data, disableAnim)
        return data


class ConditionBuilder(DataBuilder):
    __slots__ = ('_defaultLinkage',)

    def __init__(self, tooltipType, linkage, defaultLinkage, provider):
        super(ConditionBuilder, self).__init__(tooltipType, linkage, provider)
        self._defaultLinkage = defaultLinkage

    def build(self, formatType, advanced_, *args, **kwargs):
        data = self._buildData(advanced_, *args, **kwargs)
        if self._check(data):
            linkage = self._linkage
        else:
            data = self._format(data, formatType)
            linkage = self._defaultLinkage
        return (self._provider, data, linkage)

    def _format(self, data, formatType):
        return complex_formatters.doFormatData(data['data'], formatType)

    def _check(self, data):
        raise NotImplementedError


class DefaultFormatBuilder(ConditionBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, defaultLinkage, provider):
        super(DefaultFormatBuilder, self).__init__(tooltipType, '', defaultLinkage, provider)

    def _check(self, data):
        return False


class ComplexBuilder(AdvancedBuilder):
    __slots__ = ('advanced_ComplexTooltip',)

    def __init__(self, tooltipType, linkage, advancedComplexTooltips):
        super(ComplexBuilder, self).__init__(tooltipType, linkage)
        self.advancedComplexTooltips = advancedComplexTooltips

    def supportAdvanced(self, tooltipType, *args):
        return tooltipType in self.advancedComplexTooltips

    def build(self, formatType, advanced_, *args, **kwargs):
        data = complex_formatters.doFormatToolTip(args[0], formatType)
        linkage = self._linkage
        if self.supportAdvanced(*args):
            disableAnim = self._getDisableAnimFlag()
            linkage = args[0]
            item = self.advancedComplexTooltips[linkage]
            if advanced_:
                buildTooltipData = [item, linkage]
                data = advanced.ComplexAdvanced(contexts.ToolTipContext(None)).buildToolTip(buildTooltipData)
                if not disableAnim:
                    self._setDisableAnimFlag()
            else:
                data = advanced.ComplexTooltip(contexts.ToolTipContext(None), disableAnim).buildToolTip(data)
            linkage = TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI
        if data:
            return (self._provider, data, linkage)
        else:
            _logger.debug('Complex tooltip %s can not be shown: %r', formatType, args)
            return (None, None, None)


class AdvancedComplexBuilder(AdvancedBuilder):

    def __init__(self, tooltipType, linkage, provider):
        super(AdvancedComplexBuilder, self).__init__(tooltipType, linkage)
        self._provider = provider

    def supportAdvanced(self, _, *args):
        linkage = args[0]
        return linkage in ADVANCED_COMPLEX_TOOLTIPS

    def build(self, formatType, advanced_, *args, **kwargs):
        disableAnim = self._getDisableAnimFlag()
        linkage = args[0]
        supportAdvanced = self.supportAdvanced(self.tooltipType, linkage)
        if advanced_ and supportAdvanced:
            item = ADVANCED_COMPLEX_TOOLTIPS[linkage]
            data = advanced.ComplexAdvanced(contexts.ToolTipContext(None)).buildToolTip((item, linkage))
            if not disableAnim:
                self._setDisableAnimFlag()
        else:
            data = self._provider.buildToolTip(*args)
            if supportAdvanced:
                self._provider.addAdvancedBlock(data, disableAnim)
        return (self._provider, data, self._linkage)


class BuildersCollection(object):
    __slots__ = ('_builders',)

    def __init__(self, *builders):
        super(BuildersCollection, self).__init__()
        self._builders = {builder.tooltipType:builder for builder in builders}

    def clear(self):
        self._builders.clear()

    @property
    def linkages(self):
        return self._builders.keys()

    @property
    def total(self):
        return len(self._builders)

    def addBuilder(self, builder):
        type_ = builder.tooltipType
        if type_ not in self._builders:
            self._builders[type_] = builder
        else:
            raise SoftException('Builder with type {} is already added'.format(type_))

    def getBuilder(self, tooltipType):
        return self._builders[tooltipType] if tooltipType in self._builders else None


class LazyBuildersCollection(BuildersCollection):

    def __init__(self, settings, *builders):
        super(LazyBuildersCollection, self).__init__(*builders)
        self._settings = settings

    def clear(self):
        super(LazyBuildersCollection, self).clear()
        self._settings = None
        return

    def getBuilder(self, linkage):
        builder = super(LazyBuildersCollection, self).getBuilder(linkage)
        if builder is None:
            builder = self._load(linkage)
        return builder

    def _load(self, tooltipType):
        for path, tooltipTypes in self._settings:
            if tooltipType not in tooltipTypes:
                continue
            imported = importlib.import_module(path)
            try:
                builders = imported.getTooltipBuilders()
            except AttributeError:
                raise SoftException('Package {0} does not have method "getTooltipBuilders", or when calling "getTooltipBuilders", it failed to instantiate one of the builders.'.format(path))

            for builder in builders:
                if builder.tooltipType not in tooltipTypes:
                    raise SoftException('Type "{}" is not found in tooltips settings {} in {}'.format(builder.tooltipType, tooltipTypes, path))
                self.addBuilder(builder)

            return self._builders[tooltipType]

        return None
