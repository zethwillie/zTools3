gMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar')

cmds.progressBar( gMainProgressBar,
				edit=True,
				beginProgress=True,
				isInterruptable=True,
				status='"Example Calculation ...',
				maxValue=5000 )

for i in range(5000) :
	if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True ) :
		break

	cmds.progressBar(gMainProgressBar, edit=True, step=1)

cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)