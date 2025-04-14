"""
브로커 패턴 테스트 실행 스크립트

기능:
1. 테스트 환경 설정: 필요한 환경 변수 및 경로 설정
2. 테스트 케이스 수집: 모든 테스트 케이스 또는 지정된 테스트 수집
3. 테스트 실행: 단위 및 통합 테스트 실행
4. 결과 보고: 테스트 결과 출력 및 요약

테스트 실행 방법:
- 모든 테스트 실행: python -m test.run_broker_tests
- 특정 테스트 실행: python -m test.run_single_test [test_name]
"""

import unittest
from test.test_broker_pattern import TestBrokerPattern

if __name__ == "__main__":
    # 테스트 스위트 생성
    test_suite = unittest.TestSuite()
    
    # 테스트 케이스 추가 (수정된 부분)
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestBrokerPattern))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)
    
    print("브로커 패턴 테스트 완료") 