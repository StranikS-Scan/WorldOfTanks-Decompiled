# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/history_manager/commands/new_year/ny_return_to_view.py
from gui.impl.new_year.history_manager.commands.return_to_view import ReturnToView
from gui.impl.new_year.navigation import NewYearNavigation

class NyReturnToView(ReturnToView):

    def execute(self):
        context = self.getContext()
        NewYearNavigation.switchToView(**context)
