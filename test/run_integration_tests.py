import unittest
from test.test_broker_integration import TestBrokerIntegration

if __name__ == "__main__":
    # 테스트 로더 생성
    loader = unittest.TestLoader()
    
    # 통합 테스트 스위트 생성
    test_suite = loader.loadTestsFromTestCase(TestBrokerIntegration)
    
    # 테스트 실행기 생성 및 실행
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)
    
    print("브로커 패턴 통합 테스트 완료") 