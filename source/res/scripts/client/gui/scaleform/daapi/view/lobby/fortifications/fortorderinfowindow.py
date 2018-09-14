# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortOrderInfoWindow.py
from helpers.i18n import makeString as _ms
from constants import MAX_FORTIFICATION_LEVEL
from gui.shared.formatters import text_styles
from gui.shared.fortifications.FortOrder import FortOrder
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortOrderInfoWindowMeta import FortOrderInfoWindowMeta

def _newLine(fontSize):
    return "<font size='%d'><br><br></font>" % fontSize


class FortOrderInfoWindow(FortOrderInfoWindowMeta, FortViewHelper):

    def __init__(self, ctx = None):
        super(FortOrderInfoWindow, self).__init__()
        raise 'orderID' in ctx or AssertionError
        self.__orderID = ctx['orderID']
        self.__order = self.fortCtrl.getFort().getOrder(self.__orderID)

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(FortOrderInfoWindow, self)._populate()
        self.as_setWindowDataS({'windowTitle': self.__order.userName,
         'panelTitle': text_styles.middleTitle('#fortifications:fortConsumableOrder/battleParams'),
         'orderDescrTitle': text_styles.middleTitle('#fortifications:fortConsumableOrder/titleDescr'),
         'btnLbl': _ms('#fortifications:Orders/orderPopover/closeButton'),
         'orderDescrBody': text_styles.main(self.__order.getOperationDescription())})
        fmtLvl = text_styles.main(_ms('#fortifications:fortConsumableOrder/params/level_lbl', level=fort_formatters.getTextLevel(self.__order.level)))
        self.as_setDynPropertiesS({'orderIcon': self.__order.icon,
         'level': self.__order.level,
         'orderLevel': fmtLvl,
         'orderTitle': self.__order.userName,
         'orderParams': self.__makeParams()})

    def __makeParams(self):
        result = []
        orderLevel = self.__order.level
        columns = range(min(3, MAX_FORTIFICATION_LEVEL - orderLevel + 1))
        for column in columns:
            result.append(self.__makeColumnParamValues(orderLevel + column, column == 0, isShowSeparator=column != len(columns) - 1))

        result.append(self.__makeColumnParamLabels())
        return result

    def __makeColumnParamValues(self, level, isCurrentLevel = False, isShowSeparator = True):
        battleOrder = FortOrder(self.__orderID, level=level)
        if isCurrentLevel:
            paramsStyle, levelStyle = text_styles.stats, text_styles.neutral
        else:
            paramsStyle = levelStyle = text_styles.disabled
        levelStr = _ms('#fortifications:fortConsumableOrder/levelLbl', level=fort_formatters.getTextLevel(level))
        return {'params': paramsStyle(_newLine(2).join(map(str, dict(battleOrder.getParams()).values()))),
         'orderLevel': levelStyle(levelStr),
         'isShowSeparator': isShowSeparator}

    def __makeColumnParamLabels(self):
        params = []
        for paramKey in dict(self.__order.getParams()).iterkeys():
            params.append(_ms('#menu:moduleInfo/params/%s' % paramKey))

        return {'params': text_styles.main(_newLine(1).join(params)),
         'orderLevel': None,
         'isShowSeparator': False}
