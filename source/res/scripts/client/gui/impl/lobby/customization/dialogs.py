# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/dialogs.py
from BWUtil import AsyncReturn
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.gf_builders import ConfirmCancelDialogBuilder, WarningDialogBuilder
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons
from items.components.c11n_constants import SeasonType
from th_async import th_async, th_await
_R_APPLY_TO_OTHER_SEASONS = R.strings.dialogs.customization.applyToOtherSeasons
_R_APPLY_TO_OTHER_SEASON = R.strings.dialogs.customization.applyToOtherSeason
_R_SEASONS_REMOVE = {SeasonType.SUMMER: _R_APPLY_TO_OTHER_SEASON.summer,
 SeasonType.WINTER: _R_APPLY_TO_OTHER_SEASON.winter,
 SeasonType.DESERT: _R_APPLY_TO_OTHER_SEASON.desert,
 SeasonType.SUMMER | SeasonType.WINTER: _R_APPLY_TO_OTHER_SEASONS.summer_winter,
 SeasonType.WINTER | SeasonType.DESERT: _R_APPLY_TO_OTHER_SEASONS.winter_desert,
 SeasonType.SUMMER | SeasonType.DESERT: _R_APPLY_TO_OTHER_SEASONS.summer_desert}
_DIMMER_ALPHA = 0.8

@th_async
def showApplyToOtherSeasonsDialog(lockedSeasons):
    seasons, removed, these, message = getDataForApplyToOtherSeasonsMessage(lockedSeasons)
    description = backport.text(message, season=seasons, removed=removed, this=these)
    builder = WarningDialogBuilder()
    builder.setTitle(_R_APPLY_TO_OTHER_SEASONS.title())
    builder.setDescription(description)
    builder.setConfirmButtonLabel(_R_APPLY_TO_OTHER_SEASONS.submit())
    builder.setCancelButtonLabel(_R_APPLY_TO_OTHER_SEASONS.cancel())
    builder.setFocusedButtonID(DialogButtons.CANCEL)
    builder.setDimmerAlpha(_DIMMER_ALPHA)
    result = yield th_await(dialogs.show(builder.build()))
    raise AsyncReturn(result.result in DialogButtons.ACCEPT_BUTTONS)


def getDataForApplyToOtherSeasonsMessage(lockedSeasons):
    seasonsMask = reduce(int.__or__, lockedSeasons, SeasonType.UNDEFINED)
    rSeasons = _R_SEASONS_REMOVE.get(seasonsMask, R.invalid)
    seasons = (backport.text(rSeasons()) if rSeasons.exists() else '').upper()
    removed = backport.text(_R_APPLY_TO_OTHER_SEASONS.removed()).upper()
    these = backport.text(_R_APPLY_TO_OTHER_SEASONS.these()) if len(lockedSeasons) > 1 else backport.text(_R_APPLY_TO_OTHER_SEASONS.this())
    message = _R_APPLY_TO_OTHER_SEASONS.message() if len(lockedSeasons) > 1 else _R_APPLY_TO_OTHER_SEASON.message()
    return (seasons,
     removed,
     these,
     message)


@th_async
def showCloseConfirmWithoutApplyingChangesDialog():
    rCloseConfirm = R.strings.dialogs.customization.close
    builder = ConfirmCancelDialogBuilder()
    builder.setTitle(rCloseConfirm.title())
    builder.setConfirmButtonLabel(rCloseConfirm.submit())
    builder.setCancelButtonLabel(rCloseConfirm.cancel())
    builder.setFocusedButtonID(DialogButtons.CANCEL)
    builder.setDimmerAlpha(_DIMMER_ALPHA)
    result = yield th_await(dialogs.show(builder.build()))
    raise AsyncReturn(result.result in DialogButtons.ACCEPT_BUTTONS)
