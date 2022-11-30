# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/ny/mixins.py
from gui.impl.new_year.navigation import NewYearNavigation
from uilogging.ny.loggers import NySelectableObjectLogger, NySelectableObjectFlowLogger

class SelectableObjectLoggerMixin(object):
    __selectableObjectLogger = NySelectableObjectLogger()
    __flowUILogger = NySelectableObjectFlowLogger()

    def logClick(self, anchorName):
        currentObject = NewYearNavigation.getCurrentObject()
        self.__selectableObjectLogger.logClick(anchorName, currentObject)
        self.__flowUILogger.logClick(anchorName, currentObject)
