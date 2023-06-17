import zTools3.rig.zbw_rigger_utils as zrt
import importlib
import zTools3.rig.zbw_rigger_baseLimb as BL
import zTools3.rig.zbw_rig as rig
import zTools3.rig.zbw_rigger_window as zrw


class ArmRigUI(zrw.RiggerWindow):
    def __init__(self):
        self.width = 300
        self.height = 600

        self.winInitName = "zbw_armRiggerUI"
        self.winTitle = "Arm Rigger UI"
        # common
        self.defaultLimbName = "arm"
        self.defaultOrigPrefix = "L"
        self.defaultMirPrefix = "R"
        self.pts = [(5, 20, 0), (15, 20, -1), (25, 20, 0), (27, 20, 0)]
        self.baseNames = ["shoulder", "elbow", "wrist", "wristEnd"]
        self.secRotOrderJnts = [2]
        self.make_UI()

    def create_rigger(self, *args):
        self.rigger = ArmRig()
        self.get_values_for_rigger()
        self.set_values_for_rigger()


class ArmRig(BL.BaseLimb):

    def __init__(self):
        BL.BaseLimb.__init__(self)
