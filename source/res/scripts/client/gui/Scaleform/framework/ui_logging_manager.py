# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/ui_logging_manager.py
from gui.Scaleform.framework.entities.abstract.UILoggerManagerMeta import UILoggerManagerMeta
from gui.shared.utils import flashObject2Dict
from helpers import dependency
from skeletons.ui_logging import IUILoggingCore
from wotdecorators import noexcept

class UILoggerManager(UILoggerManagerMeta):
    _logger = dependency.descriptor(IUILoggingCore)

    @noexcept
    def onLog(self, feature, group, action, logLevel, params):
        self._logger.log(feature, group, action, logLevel, **flashObject2Dict(params))
