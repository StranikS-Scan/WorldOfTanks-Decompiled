# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/buffs_notification_panel.py
from __future__ import absolute_import
from halloween.skeletons.halloween_anomalies_controller import IHalloweenAnomaliesController
from halloween_common.halloween_constants import AnomalyType
from helpers import dependency
from gui import makeHtmlString
from gui.impl.gen import R
from gui.impl import backport
from gui.battle_control.controllers.battle_hints.component import BattleHintComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID, HALLOWEEN_BATTLE_HINTS_QUEUE_ID
from halloween.gui.scaleform.daapi.view.battle.anomalies_utils import anomalyTitle, anomalyDescriptionList
from halloween.gui.scaleform.daapi.view.meta.BuffNotificationSystemMeta import BuffNotificationSystemMeta

class BuffsNotificationSystem(BattleHintComponent, BuffNotificationSystemMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    hwAnomaliesCtrl = dependency.descriptor(IHalloweenAnomaliesController)
    ICONS_PATH = R.images.halloween.gui.maps.icons.anomalies.s_58x58
    BATTLE_HINT_TEMPLATE = 'halloween.buffNotification'

    def __init__(self):
        super(BuffsNotificationSystem, self).__init__(battleHintsQueueParams=HALLOWEEN_BATTLE_HINTS_QUEUE_ID)

    def _populate(self):
        hwBattleGuiCtrl = self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.initIgnoreBuffNotification()

    def _dispose(self):
        hwBattleGuiCtrl = self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.clearIgnoreBuffNotification()

    def _showHint(self, model, params):
        anomalyID = params['buffKey']
        anomalyData = self.hwAnomaliesCtrl.getAnomalyByID(anomalyID)
        isSecret = anomalyData and anomalyData.type == AnomalyType.SECRET
        hintData = {'iconSource': backport.image(self.ICONS_PATH.dyn(anomalyID)()),
         'title': anomalyTitle(anomalyID, isSecret=isSecret),
         'info': anomalyDescriptionList(anomalyID, isSecret=isSecret)}
        hwBattleGuiCtrl = self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onShowPanelBuffNotification(True)
        self.as_showBuffNotificationS(hintData)

    def _hideHint(self):
        hwBattleGuiCtrl = self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onShowPanelBuffNotification(False)
        self.as_hideBuffNotificationS()

    def _cancelFadeOut(self):
        self.as_cancelFadeOutS()

    def __makeHtmlFormat(self, text, format):
        return makeHtmlString('html_templates:battle/textStyle', format, {'text': text})
