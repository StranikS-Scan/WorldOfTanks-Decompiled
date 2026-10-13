# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/tooltips/shell_tooltip.py
from portal.gui.impl.gen.view_models.views.lobby.tooltips.portal_shell_stat import PortalShellStat
from frameworks.wulf import ViewSettings
from portal.gui.impl.gen.view_models.views.lobby.tooltips.shell_tooltip_model import ShellTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from items import vehicles

class ShellTooltip(ViewImpl):
    __slots__ = ('_vehicle',)

    def __init__(self, vehicle):
        settings = ViewSettings(R.views.portal.lobby.tooltips.ShellTooltip())
        settings.model = ShellTooltipModel()
        self._vehicle = vehicle
        super(ShellTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ShellTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ShellTooltip, self)._onLoading(*args, **kwargs)
        self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as vm:
            self.__fillModel(vm)

    def __fillModel(self, model):
        self._fillShellInfo(model)
        self._fillStats(model.getStats())

    def _fillShellInfo(self, model):
        shellDescr = vehicles.getItemByCompactDescr(self._vehicle.shells.installed[0].intCD)
        model.setName(self._vehicle.shells.installed[0].userName)
        model.setType(self._vehicle.shells.installed[0].type)
        model.setCaliber(shellDescr.caliber)

    def _fillStats(self, array):
        array.clear()
        shellDescr = vehicles.getItemByCompactDescr(self._vehicle.shells.installed[0].intCD)
        damageLimits = shellDescr.randomizationDmgLimits
        pPower = self._vehicle.gun.descriptor.shots[0].piercingPower
        speed = self._vehicle.gun.descriptor.shots[0].speed
        stats = [{'from': damageLimits[0],
          'to': damageLimits[1],
          'name': 'damage'}, {'from': pPower[1],
          'to': pPower[0],
          'name': 'armor_penetration'}, {'from': speed,
          'to': 0,
          'name': 'flight_speed'}]
        for stat in stats:
            statModel = PortalShellStat()
            statModel.setFrom(stat['from'])
            statModel.setTo(stat['to'])
            statModel.setName(stat['name'])
            array.addViewModel(statModel)

        array.invalidate()
