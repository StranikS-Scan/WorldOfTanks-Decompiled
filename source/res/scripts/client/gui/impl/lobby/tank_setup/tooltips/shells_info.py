# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/tooltips/shells_info.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.shell_info_model import ShellInfoModel
from gui.impl.gen.view_models.views.lobby.tooltips.shells_info_model import ShellsInfoModel
from gui.impl.gen.view_models.views.lobby.tooltips.shells_specification_model import ShellsSpecificationModel
from gui.impl.pub import ViewImpl
from gui.shared.items_parameters import params_helper
from gui.shared.items_parameters.formatters import MEASURE_UNITS, formatParameter
from helpers import i18n
_SHELLS_INFO_PARAMS = ('avgDamage', 'avgPiercingPower', 'shotSpeed', 'explosionRadius', 'stunMaxDuration')

class ShellsInfo(ViewImpl):

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = ShellsInfoModel()
        settings.args = args
        settings.kwargs = kwargs
        super(ShellsInfo, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ShellsInfo, self).getViewModel()

    def _onLoading(self, vehicle, isInstalled=True):
        super(ShellsInfo, self)._onLoading()
        with self.viewModel.transaction() as tx:
            tx.setMaxCount(vehicle.ammoMaxSize)
            tx.setIsAutoRenewalEnabled(vehicle.isAutoLoad)
            shellsParams = []
            totalCount = 0
            shellsLayout = vehicle.shells.installed if isInstalled else vehicle.shells.layout
            for shell in shellsLayout:
                if shell is None:
                    continue
                shellModel = ShellInfoModel()
                shellModel.setName(shell.userName)
                shellModel.setType(shell.type)
                shellModel.setCount(shell.count)
                shellModel.setImageSource(R.images.gui.maps.icons.shell.medium.dyn(shell.type)())
                shellsParams.append(params_helper.getParameters(shell, vehicle.descriptor))
                tx.getShells().addViewModel(shellModel)
                totalCount += shell.count

            tx.setInstalledCount(totalCount)
            for paramName in _SHELLS_INFO_PARAMS:
                specificationModel = ShellsSpecificationModel()
                specificationModel.setParamName(paramName)
                specificationModel.setMetricValue(i18n.makeString(MEASURE_UNITS.get(paramName, '')))
                for shellParam in shellsParams:
                    value = formatParameter(paramName, shellParam.get(paramName))
                    specificationModel.getValues().addString('' if value is None else value)

                tx.getSpecifications().addViewModel(specificationModel)

        return
