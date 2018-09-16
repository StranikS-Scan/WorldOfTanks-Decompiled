# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/builders.py
import importlib
import logging
from gui.shared.tooltips import complex_formatters
_logger = logging.getLogger(__name__)

class TooltipBuilder(object):
    __slots__ = ('_tooltipType', '_linkage')

    def __init__(self, tooltipType, linkage):
        super(TooltipBuilder, self).__init__()
        self._tooltipType = tooltipType
        self._linkage = linkage

    @property
    def tooltipType(self):
        return self._tooltipType

    @property
    def linkage(self):
        return self._linkage

    def build(self, manager, stateType, *args):
        raise NotImplementedError


class SimpleBuilder(TooltipBuilder):
    __slots__ = ()

    def build(self, manager, stateType, *args):
        manager.show(args, self._linkage)
        return None


class DataBuilder(SimpleBuilder):
    __slots__ = ('_provider',)

    def __init__(self, tooltipType, linkage, provider):
        super(DataBuilder, self).__init__(tooltipType, linkage)
        self._provider = provider

    def build(self, manager, formatType, *args):
        data = self._buildData(*args)
        manager.show(data, self._linkage)
        return self._provider

    def _buildData(self, *args):
        return self._provider.buildToolTip(*args)


class ConditionBuilder(DataBuilder):
    __slots__ = ('_defaultLinkage',)

    def __init__(self, tooltipType, linkage, defaultLinkage, provider):
        super(ConditionBuilder, self).__init__(tooltipType, linkage, provider)
        self._defaultLinkage = defaultLinkage

    def build(self, manager, formatType, *args):
        data = self._buildData(*args)
        if self._check(data):
            manager.show(data, self._linkage)
        else:
            data = self._format(data, formatType)
            if data:
                manager.show(data, self._defaultLinkage)
        return self._provider

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


class ComplexBuilder(TooltipBuilder):
    __slots__ = ()

    def build(self, manager, formatType, *args):
        data = complex_formatters.doFormatToolTip(args[0], formatType)
        if data:
            manager.show(data, self._linkage)
        else:
            _logger.debug('Complex tooltip %s can not be shown: %r', formatType, args)
        return None


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
            raise UserWarning('Builder with type {} is already added'.format(type_))

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
                raise UserWarning('Package {0} does not have method getTooltipBuilders'.format(path))

            for builder in builders:
                if builder.tooltipType not in tooltipTypes:
                    raise UserWarning('Type "{}" is not found in tooltips settings {} in {}'.format(builder.tooltipType, tooltipTypes, path))
                self.addBuilder(builder)

            return self._builders[tooltipType]

        return None
