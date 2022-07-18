import unittest
import zTools.rig.zbw_rig as rig


class ZbwRigTestMethods(unittest.TestCase):
    def setUp(self):
        print("Setting up the tests")
        # open a maya headless scene


    def test_linear_interpolate_scalar(self):
        A = 0
        B = 4

        self.assertEqual(rig.linear_interpolate_scalar(A, B, .5), 2)
        self.assertEqual(rig.linear_interpolate_scalar(A, B, .0), 0)
        self.assertEqual(rig.linear_interpolate_scalar(A, B, 1), 4)


    def tearDown(self):
        print("Tearing down the tests")

# suite = unittest.TestLoader().loadTestsFromTestCase(RigTestMethods)
# unittest.TextTestRunner(verbosity=2).run(suite)