import unittest
from unittest.mock import MagicMock, patch
from client.client import Client
from client.client_proxy import ClientProxy
from common.message import Request, Response

class TestClientProxy(unittest.TestCase):
    """클라이언트 프록시 테스트"""
    
    def setUp(self):
        """테스트 사전 준비"""
        # 브로커 모의 구현
        self.mock_broker = MagicMock()
        
        # 성공 응답 설정
        success_response = Response(result="test_result")
        self.mock_broker.forward_request.return_value = success_response
        
        # 클라이언트 프록시 생성
        self.client_proxy = ClientProxy(
            broker=self.mock_broker,
            service_name="TestService"
        )
    
    def test_call_method(self):
        """메서드 호출 테스트"""
        # 메서드 호출
        result = self.client_proxy.call_method("test_method", arg1="value1", arg2=42)
        
        # 결과 확인
        self.assertEqual(result, "test_result")
        
        # 브로커에 요청 전달 확인
        self.mock_broker.forward_request.assert_called_once()
        request = self.mock_broker.forward_request.call_args[0][0]
        self.assertEqual(request.service_name, "TestService")
        self.assertEqual(request.method_name, "test_method")
        self.assertEqual(request.parameters, {"arg1": "value1", "arg2": 42})
    
    def test_dynamic_method_call(self):
        """동적 메서드 호출 테스트 (__getattr__ 사용)"""
        # 동적 메서드 호출
        result = self.client_proxy.dynamic_method(param1="value1", param2="value2")
        
        # 결과 확인
        self.assertEqual(result, "test_result")
        
        # 브로커에 요청 전달 확인
        self.mock_broker.forward_request.assert_called_once()
        request = self.mock_broker.forward_request.call_args[0][0]
        self.assertEqual(request.method_name, "dynamic_method")
        self.assertEqual(request.parameters, {"param1": "value1", "param2": "value2"})
    
    def test_error_response(self):
        """오류 응답 처리 테스트"""
        # 오류 응답 설정
        error_response = Response(error="test_error")
        self.mock_broker.forward_request.return_value = error_response
        
        # 메서드 호출 시 예외 발생 확인
        with self.assertRaises(Exception) as context:
            self.client_proxy.call_method("test_method")
            
        # 예외 메시지 확인
        self.assertIn("test_error", str(context.exception))

class TestClient(unittest.TestCase):
    """클라이언트 테스트"""
    
    def setUp(self):
        """테스트 사전 준비"""
        # 브로커 모의 구현
        self.mock_broker = MagicMock()
        self.mock_broker.list_services.return_value = ["Service1", "Service2"]
        
        # 클라이언트 생성
        self.client = Client(self.mock_broker)
    
    def test_list_services(self):
        """서비스 목록 조회 테스트"""
        # 서비스 목록 조회
        services = self.client.list_services()
        
        # 결과 확인
        self.assertEqual(services, ["Service1", "Service2"])
        self.mock_broker.list_services.assert_called_once()
    
    def test_get_service_success(self):
        """존재하는 서비스 조회 테스트"""
        # 서비스 조회
        service_proxy = self.client.get_service("Service1")
        
        # 결과 확인
        self.assertIsNotNone(service_proxy)
        self.assertIsInstance(service_proxy, ClientProxy)
        self.assertEqual(service_proxy.service_name, "Service1")
        
        # 캐싱 테스트
        service_proxy2 = self.client.get_service("Service1")
        self.assertIs(service_proxy, service_proxy2)  # 동일 객체여야 함
    
    def test_get_service_not_found(self):
        """존재하지 않는 서비스 조회 테스트"""
        # 존재하지 않는 서비스 조회
        service_proxy = self.client.get_service("UnknownService")
        
        # 결과 확인
        self.assertIsNone(service_proxy)

if __name__ == "__main__":
    unittest.main() 