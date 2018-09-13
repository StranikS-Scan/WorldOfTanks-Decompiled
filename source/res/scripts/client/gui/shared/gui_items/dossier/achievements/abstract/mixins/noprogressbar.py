# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/abstract/mixins/NoProgressBar.py


class NoProgressBar(object):

    def _readLevelUpTotalValue(self, dossier):
        return 0

    def _readLevelUpValue(self, dossier):
        return 0
