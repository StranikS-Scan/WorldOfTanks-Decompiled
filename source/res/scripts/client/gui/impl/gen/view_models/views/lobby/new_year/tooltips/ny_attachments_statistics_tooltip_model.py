# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_attachments_statistics_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_loot_box_statistics_attachment_model import NyLootBoxStatisticsAttachmentModel

class NyAttachmentsStatisticsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NyAttachmentsStatisticsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getAttachments(self):
        return self._getArray(0)

    def setAttachments(self, value):
        self._setArray(0, value)

    @staticmethod
    def getAttachmentsType():
        return NyLootBoxStatisticsAttachmentModel

    def _initialize(self):
        super(NyAttachmentsStatisticsTooltipModel, self)._initialize()
        self._addArrayProperty('attachments', Array())
