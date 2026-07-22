# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/preferred_map_slot_reward_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.preferred_map_slot_reward_tooltip_model import PreferredMapSlotRewardTooltipModel
from gui.impl.lobby.premacc.views_helpers import getResolvedSlotByTypeName
from gui.impl.pub import ViewImpl
from gui.shared.system_factory import registerWulfTooltipContentFactory

class PreferredMapSlotTooltip(ViewImpl):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.tooltips.PreferredMapSlotRewardTooltip())
        settings.model = PreferredMapSlotRewardTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(PreferredMapSlotTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PreferredMapSlotTooltip, self).getViewModel()

    def _onLoading(self, slotName, amount=0, *args, **kwargs):
        super(PreferredMapSlotTooltip, self)._onLoading(*args, **kwargs)
        slotName, amount = _unpackPreferredMapSlotTooltipArgs(slotName, amount, *args)
        slot = getResolvedSlotByTypeName(slotName)
        expire = slot.expire if slot is not None else 0
        with self.viewModel.transaction() as model:
            model.setSlotName(slotName)
            model.setAmountDay(amount)
            model.setExpire(int(expire) if expire < float('inf') else 0)
        return


def _createPreferredMapSlotTooltip(view, event):
    getTooltipData = getattr(view, 'getTooltipData', None)
    if getTooltipData is None:
        return
    else:
        tooltipData = getTooltipData(event)
        return None if tooltipData is None else PreferredMapSlotTooltip(*tooltipData.specialArgs)


def _unpackPreferredMapSlotTooltipArgs(slotName, amount=0, *extraArgs):
    if isinstance(slotName, basestring) and ':' in slotName:
        slotName, _, amountStr = slotName.partition(':')
        slotName = slotName.strip()
        amount = amountStr.strip() or amount
    if isinstance(slotName, (list, tuple)):
        if len(slotName) >= 2:
            amount = slotName[1]
            slotName = slotName[0]
        elif len(slotName) == 1:
            slotName = slotName[0]
    if not amount and extraArgs:
        amount = extraArgs[0]
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        amount = 0

    return (slotName, amount)


registerWulfTooltipContentFactory(R.views.lobby.tooltips.PreferredMapSlotRewardTooltip(), _createPreferredMapSlotTooltip)
