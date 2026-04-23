# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_meta_view/bundle_bonus_model.py
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.bonus_model import BonusModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import DialogTemplateGenericTooltipViewModel

class BundleBonusModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(BundleBonusModel, self).__init__(properties=properties, commands=commands)

    @property
    def tooltip(self):
        return self._getViewModel(9)

    @staticmethod
    def getTooltipType():
        return DialogTemplateGenericTooltipViewModel

    def getIconName(self):
        return self._getString(10)

    def setIconName(self, value):
        self._setString(10, value)

    def getAmount(self):
        return self._getNumber(11)

    def setAmount(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(BundleBonusModel, self)._initialize()
        self._addViewModelProperty('tooltip', DialogTemplateGenericTooltipViewModel())
        self._addStringProperty('iconName', '')
        self._addNumberProperty('amount', 0)
