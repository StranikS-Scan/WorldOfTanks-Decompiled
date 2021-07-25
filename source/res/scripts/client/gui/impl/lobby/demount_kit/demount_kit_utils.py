# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/demount_kit/demount_kit_utils.py
import typing
from gui.impl import backport
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.artefacts import OptionalDevice

def getDemountDialogTitle(item, forFitting=False, fromSlot=False):
    titleRes = R.strings.demount_kit.equipmentDemountFromSlot if fromSlot else R.strings.demount_kit.equipmentDemount
    titleRes = titleRes.confirmationForFitting.title if forFitting else titleRes.confirmation.title
    return backport.text(titleRes(), equipment=item.userName)
