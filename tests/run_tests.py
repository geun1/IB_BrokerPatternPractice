import unittest
import sys
import os

# 상위 디렉토리 경로 추가 (모듈 임포트를 위함)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 테스트 모듈 가져오기
from tests.test_serializer import TestSerializer
from tests.test_message import TestMessage
from tests.test_broker import TestServiceRepository, TestBroker
from tests.test_server import TestServerProxy, TestServer
from tests.test_client import TestClientProxy, TestClient
from tests.test_integration import TestIntegration

def run_all_tests():
    """
    모든 테스트 실행
    """
    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 추가
    suite.addTests(loader.loadTestsFromTestCase(TestSerializer))
    suite.addTests(loader.loadTestsFromTestCase(TestMessage))
    suite.addTests(loader.loadTestsFromTestCase(TestServiceRepository))
    suite.addTests(loader.loadTestsFromTestCase(TestBroker))
    suite.addTests(loader.loadTestsFromTestCase(TestServerProxy))
    suite.addTests(loader.loadTestsFromTestCase(TestServer))
    suite.addTests(loader.loadTestsFromTestCase(TestClientProxy))
    suite.addTests(loader.loadTestsFromTestCase(TestClient))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 테스트 결과 출력
    print("\n=== 테스트 요약 ===")
    print(f"실행된 테스트: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    
    # 실패 또는 오류가 있으면 종료 코드 1 반환
    return 0 if result.wasSuccessful() else 1

def run_specific_test(test_name):
    """
    특정 테스트 모듈만 실행
    
    Args:
        test_name: 실행할 테스트 모듈 이름 (예: "serializer", "message" 등)
    """
    test_modules = {
        "serializer": TestSerializer,
        "message": TestMessage,
        "broker": [TestServiceRepository, TestBroker],
        "server": [TestServerProxy, TestServer],
        "client": [TestClientProxy, TestClient],
        "integration": TestIntegration
    }
    
    if test_name not in test_modules:
        print(f"오류: '{test_name}' 테스트 모듈을 찾을 수 없습니다.")
        print(f"사용 가능한 테스트 모듈: {', '.join(test_modules.keys())}")
        return 1
    
    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 추가
    test_classes = test_modules[test_name]
    if isinstance(test_classes, list):
        for test_class in test_classes:
            suite.addTests(loader.loadTestsFromTestCase(test_class))
    else:
        suite.addTests(loader.loadTestsFromTestCase(test_classes))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 실패 또는 오류가 있으면 종료 코드 1 반환
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    # 명령행 인수 확인
    if len(sys.argv) > 1:
        # 특정 테스트 모듈 실행
        test_name = sys.argv[1].lower()
        sys.exit(run_specific_test(test_name))
    else:
        # 모든 테스트 실행
        sys.exit(run_all_tests()) 