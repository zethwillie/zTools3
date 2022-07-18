import unittest

def run():
    print("getting tests. . . ")
    test_loader = unittest.TestLoader()
    tests = test_loader.discover('zTools.tests', pattern='test_*.py')
    print(("tests: ", tests))
    test_runner = unittest.runner.TextTestRunner()
    test_runner.run(tests)

if __name__ == "__main__":
    run()