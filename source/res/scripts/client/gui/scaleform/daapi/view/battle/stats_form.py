# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/stats_form.py
import BigWorld
from constants import FLAG_ACTION
from external_strings_utils import unicode_from_utf8, normalized_unicode_trim
from gui import makeHtmlString
from gui.Scaleform.daapi.view.battle import getColorValue, findHTMLFormat
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI

class _StatsForm(object):

    def __init__(self, parentUI, swf):
        self._ui = parentUI
        self._swf = swf

    def populate(self):
        self._ui.movie.preinitializeStatsView(self._swf)

    def destroy(self):
        self._ui = None
        return

    def getFormattedStrings(self, vInfoVO, vStatsVO, viStatsVO, ctx, fullPlayerName):
        format = self._findPlayerHTMLFormat(vInfoVO, ctx, self._ui.colorManager)
        unicodeStr, _ = unicode_from_utf8(fullPlayerName)
        if len(unicodeStr) > ctx.labelMaxLength:
            fullPlayerName = '{0}..'.format(normalized_unicode_trim(fullPlayerName, ctx.labelMaxLength - 2))
        fragsString = format % ' '
        if vStatsVO.frags:
            fragsString = format % str(vStatsVO.frags)
        return (format % fullPlayerName,
         fragsString,
         format % vInfoVO.vehicleType.shortName,
         ())

    def _findPlayerHTMLFormat(self, item, ctx, csManager):
        return findHTMLFormat(item, ctx, csManager)


class _FalloutStatsForm(_StatsForm):

    def __init__(self, parentUI, swf):
        super(_FalloutStatsForm, self).__init__(parentUI, swf)
        self._colorCache = {0: makeHtmlString('html_templates:battle', 'multiteamStatsPadding', {})}

    def populate(self):
        super(_FalloutStatsForm, self).populate()
        self._ui.movie.preinitializeStatsHintView('FalloutStatisticHint.swf', INGAME_GUI.TABSTATSHINT)

    def destroy(self):
        self._colorCache = None
        super(_FalloutStatsForm, self).destroy()
        return

    def getFormattedStrings(self, vInfoVO, vStatsVO, viStatsVO, ctx, fullPlayerName):
        pName, frags, vName, _ = super(_FalloutStatsForm, self).getFormattedStrings(vInfoVO, vStatsVO, viStatsVO, ctx, fullPlayerName)
        scoreFormat = self._getHTMLString('textColorGold', self._ui.colorManager)
        regularFormat = self._getHTMLString('textColorFalloutRegular', self._ui.colorManager)
        highlightedDeaths = viStatsVO.stopRespawn
        deathsFormatStyle = 'textColorFalloutHighlightedDeaths' if highlightedDeaths else 'textColorFalloutRegularDeaths'
        deathsFormat = self._getHTMLString(deathsFormatStyle, self._ui.colorManager)
        scoreString = scoreFormat % BigWorld.wg_getNiceNumberFormat(viStatsVO.winPoints)
        if viStatsVO.deathCount > 0:
            deathsString = deathsFormat % BigWorld.wg_getNiceNumberFormat(viStatsVO.deathCount)
        else:
            deathsString = deathsFormat % ''
        damageString = regularFormat % BigWorld.wg_getNiceNumberFormat(viStatsVO.damageDealt)
        resourcePointsString = regularFormat % BigWorld.wg_getNiceNumberFormat(viStatsVO.resourceAbsorbed)
        return (pName,
         frags,
         vName,
         (scoreString,
          damageString,
          deathsString,
          resourcePointsString))

    def _getHTMLString(self, colorScheme, csManager):
        color = getColorValue(colorScheme, csManager)
        if color not in self._colorCache:
            colorStr = makeHtmlString('html_templates:battle', 'multiteamStatsColoredPadding', {}).format(color)
            self._colorCache[color] = colorStr
            return colorStr
        return self._colorCache[color]

    def _findPlayerHTMLFormat(self, item, ctx, csManager):
        if ctx.isPlayerSelected(item):
            return self._getHTMLString('textColorGold', csManager)
        elif ctx.isSquadMan(item):
            return self._getHTMLString('textColorGold', csManager)
        elif ctx.isTeamKiller(item):
            return self._getHTMLString('teamkiller', csManager)
        else:
            return self._getHTMLString('textColorFalloutName', csManager)


class _MultiteamFalloutStatsForm(_FalloutStatsForm):

    def getFormattedStrings(self, vInfoVO, vStatsVO, viStatsVO, ctx, fullPlayerName):
        pName, frags, vName, (scoreString, damageString, deathsString, _) = super(_MultiteamFalloutStatsForm, self).getFormattedStrings(vInfoVO, vStatsVO, viStatsVO, ctx, fullPlayerName)
        regularFormat = self._getHTMLString('textColorFalloutRegular', self._ui.colorManager)
        flagsCaptured = viStatsVO.flagActions[FLAG_ACTION.CAPTURED]
        flagsString = regularFormat % ' '
        if flagsCaptured:
            flagsString = regularFormat % BigWorld.wg_getNiceNumberFormat(flagsCaptured)
        return (pName,
         frags,
         vName,
         (scoreString,
          damageString,
          deathsString,
          flagsString))

    def getTeamScoreFormat(self):
        return self._getHTMLString('textColorGold', self._ui.colorManager)


def statsFormFactory(parentUI, isEvent = False, isMutlipleTeams = False):
    if isEvent:
        if isMutlipleTeams:
            return _MultiteamFalloutStatsForm(parentUI, 'FalloutMultiteamStatisticForm.swf')
        return _FalloutStatsForm(parentUI, 'ResourcePointsStatisticForm.swf')
    return _StatsForm(parentUI, 'StatisticForm.swf')
