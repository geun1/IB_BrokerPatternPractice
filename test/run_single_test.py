import unittest
import sys
import time
from test.test_broker_integration import TestBrokerIntegration

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python -m test.run_single_test [test_name]")
        print("예: python -m test.run_single_test test_server_registration")
        sys.exit(1)
    
    test_name = sys.argv[1]
    suite = unittest.TestSuite()
    suite.addTest(TestBrokerIntegration(test_name))
    
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    
    # 테스트 완료 후 잠시 기다려 리소스가 정리될 시간 제공
    print("테스트 완료, 리소스 정리 중...")
    time.sleep(5) 