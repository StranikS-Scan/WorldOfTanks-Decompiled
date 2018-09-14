# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/stats_form.py
import BigWorld
from constants import FLAG_ACTION, IGR_TYPE
from external_strings_utils import unicode_from_utf8, normalized_unicode_trim
from gui import makeHtmlString
from gui.Scaleform.daapi.view.battle import getColorValue, findHTMLFormat
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.arena_info import hasResourcePoints

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
        self._colorCache = {0: '%s'}

    def populate(self):
        super(_FalloutStatsForm, self).populate()
        self._ui.movie.preinitializeStatsHintView('FalloutStatisticHint.swf', INGAME_GUI.TABSTATSHINT)

    def destroy(self):
        self._colorCache = None
        super(_FalloutStatsForm, self).destroy()
        return

    def getFormattedStrings(self, vInfoVO, vStatsVO, viStatsVO, ctx, fullPlayerName):
        padding = makeHtmlString('html_templates:battle', 'multiteamPadding', {})
        format = self._findPlayerHTMLFormat(vInfoVO, ctx, self._ui.colorManager)
        formatWithPadding = format + padding
        unicodeStr, _ = unicode_from_utf8(fullPlayerName)
        maxLabelLength = ctx.labelMaxLength
        isIGR = vInfoVO.player.isIGR()
        if isIGR:
            maxLabelLength = maxLabelLength - 2
        if len(unicodeStr) > maxLabelLength:
            fullPlayerName = '{0}..'.format(normalized_unicode_trim(fullPlayerName, maxLabelLength - 2))
        fragsString = formatWithPadding % ' '
        if vStatsVO.frags or viStatsVO.equipmentKills:
            fragsString = formatWithPadding % str(vStatsVO.frags + viStatsVO.equipmentKills)
        pName = format % fullPlayerName
        frags = fragsString
        vName = formatWithPadding % vInfoVO.vehicleType.shortName
        if isIGR:
            igrType = vInfoVO.player.igrType
            icon = makeHtmlString('html_templates:igr/iconSmall', 'premium' if igrType == IGR_TYPE.PREMIUM else 'basic')
            pName += icon
        pName += padding
        scoreFormat = self._getHTMLString('textColorGold', self._ui.colorManager) + padding
        regularFormat = self._getHTMLString('textColorFalloutRegular', self._ui.colorManager) + padding
        highlightedDeaths = viStatsVO.stopRespawn
        deathsFormatStyle = 'textColorFalloutHighlightedDeaths' if highlightedDeaths else 'textColorFalloutRegularDeaths'
        deathsFormat = self._getHTMLString(deathsFormatStyle, self._ui.colorManager) + padding
        scoreString = scoreFormat % BigWorld.wg_getNiceNumberFormat(viStatsVO.winPoints)
        if viStatsVO.deathCount > 0:
            deathsString = deathsFormat % BigWorld.wg_getNiceNumberFormat(viStatsVO.deathCount)
        else:
            deathsString = deathsFormat % ''
        damageString = regularFormat % BigWorld.wg_getNiceNumberFormat(viStatsVO.damageDealt + viStatsVO.equipmentDamage)
        if hasResourcePoints():
            specialPointsString = regularFormat % BigWorld.wg_getNiceNumberFormat(viStatsVO.resourceAbsorbed)
        else:
            flagsCaptured = viStatsVO.flagActions[FLAG_ACTION.CAPTURED]
            specialPointsString = regularFormat % BigWorld.wg_getNiceNumberFormat(flagsCaptured)
        return (pName,
         frags,
         vName,
         (scoreString,
          damageString,
          deathsString,
          specialPointsString))

    def _getHTMLString(self, colorScheme, csManager):
        color = getColorValue(colorScheme, csManager)
        if color not in self._colorCache:
            colorStr = makeHtmlString('html_templates:battle', 'multiteamStatsColoredPadding', {}).format(color)
            self._colorCache[color] = colorStr
            return colorStr
        return self._colorCache[color]

    def _findPlayerHTMLFormat(self, item, ctx, csManager):
        if ctx.isTeamKiller(item):
            return self._getHTMLString('teamkiller', csManager)
        elif ctx.isPlayerSelected(item):
            return self._getHTMLString('textColorGold', csManager)
        elif ctx.isSquadMan(item):
            return self._getHTMLString('textColorGold', csManager)
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
        padding = makeHtmlString('html_templates:battle', 'multiteamPadding', {})
        return self._getHTMLString('textColorGold', self._ui.colorManager) + padding


def statsFormFactory(parentUI, isEvent = False, isMutlipleTeams = False):
    if isEvent:
        if isMutlipleTeams:
            return _MultiteamFalloutStatsForm(parentUI, 'FalloutMultiteamStatisticForm.swf')
        return _FalloutStatsForm(parentUI, 'FalloutStatisticForm.swf')
    return _StatsForm(parentUI, 'StatisticForm.swf')
