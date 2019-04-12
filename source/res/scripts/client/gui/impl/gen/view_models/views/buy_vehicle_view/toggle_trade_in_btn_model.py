# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/buy_vehicle_view/toggle_trade_in_btn_model.py
from gui.impl.gen.view_models.ui_kit.button_icon_text_model import ButtonIconTextModel

class ToggleTradeInBtnModel(ButtonIconTextModel):
    __slots__ = ()

    def getIsRent(self):
        return self._getBool(6)

    def setIsRent(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(ToggleTradeInBtnModel, self)._initialize()
        self._addBoolProperty('isRent', False)
