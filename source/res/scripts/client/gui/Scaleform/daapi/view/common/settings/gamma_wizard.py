# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/settings/gamma_wizard.py
import BigWorld
from gui.Scaleform.daapi.view.meta.GammaWizardViewMeta import GammaWizardViewMeta
from gui.Scaleform.locale.SETTINGS import SETTINGS
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip

class GammaWizardView(GammaWizardViewMeta):
    MIN_VALUE = 0
    MAX_VALUE = 1
    DEFAULT_VALUE = 0.5

    def __init__(self, ctx=None):
        super(GammaWizardView, self).__init__(GammaWizardView)
        x = ctx.get('x', 0)
        y = ctx.get('y', 0)
        size = ctx.get('size', 0)
        self._gammaWizard = BigWorld.PyGammaWizard()
        self._currentGammaValue = 0
        self._changeGammaValue = 0
        self.updateTexture(x, y, size)
        self._gammaWizard.enable = True
        self.fireEvent(GameEvent(GameEvent.HIDE_EXTERNAL_COMPONENTS), scope=EVENT_BUS_SCOPE.GLOBAL)

    def updateTexture(self, x, y, size):
        self._gammaWizard.offsetSize = (x,
         y,
         size,
         size)

    def onApply(self):
        self._currentGammaValue = self._changeGammaValue
        self.destroy()

    def onChangeGamma(self, value):
        self._changeGammaValue = value
        self._gammaWizard.gamma = value

    def onReset(self):
        self._changeGammaValue = self.DEFAULT_VALUE

    def onClose(self):
        self._changeGammaValue = self._currentGammaValue
        self.destroy()

    def _populate(self):
        super(GammaWizardView, self)._populate()
        self._currentGammaValue = self._changeGammaValue = self._gammaWizard.gamma
        self.as_initDataS({'title': text_styles.superPromoTitle(SETTINGS.GAMMAWIZARD_TITLE),
         'header': text_styles.highlightText(SETTINGS.GAMMAWIZARD_HEADER),
         'description': text_styles.main(SETTINGS.GAMMAWIZARD_DESCRIPTION),
         'applyLabel': SETTINGS.GAMMAWIZARD_APPLY,
         'cancelLabel': SETTINGS.GAMMAWIZARD_CANCEL,
         'defaultLabel': SETTINGS.GAMMAWIZARD_DEFAULT,
         'currentValue': self._currentGammaValue,
         'gammaTooltip': makeTooltip(SETTINGS.GAMMAWIZARD_TOOLTIP_HEADER, SETTINGS.GAMMAWIZARD_TOOLTIP_BODY),
         'minValue': self.MIN_VALUE,
         'maxValue': self.MAX_VALUE,
         'defaultValue': self.DEFAULT_VALUE})

    def _dispose(self):
        self._gammaWizard.gamma = self._changeGammaValue
        self._gammaWizard.enable = False
        self.fireEvent(GameEvent(GameEvent.SHOW_EXTERNAL_COMPONENTS), scope=EVENT_BUS_SCOPE.GLOBAL)
        super(GammaWizardView, self)._dispose()
