import unittest
from test.test_broker_integration import TestBrokerIntegration

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestBrokerIntegration('test_server_registration'))
    runner = unittest.TextTestRunner()
    runner.run(suite) 