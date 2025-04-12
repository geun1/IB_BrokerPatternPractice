import unittest
from unittest.mock import MagicMock, patch
from server.server import Server
from server.server_proxy import ServerProxy
from common.message import Request, Response
from common.serializer import Serializer

class TestServerProxy(unittest.TestCase):
    """서버 프록시 테스트"""
    
    def setUp(self):
        """테스트 사전 준비"""
        # 테스트 서버 객체 모의 구현
        self.mock_server = MagicMock()
        
        # 테스트 메서드 구현
        def add(a, b):
            return a + b
            
        def fail_method():
            raise ValueError("의도적인 오류 발생")
            
        self.mock_server.add = add
        self.mock_server.fail_method = fail_method
        
        # 서버 프록시 생성
        self.server_proxy = ServerProxy(self.mock_server)
    
    def test_handle_request_success(self):
        """성공적인 요청 처리 테스트"""
        # 요청 생성
        request = Request(
            service_name="TestService",
            method_name="add",
            parameters={"a": 3, "b": 5}
        )
        
        # 요청 직렬화
        serialized_request = Serializer.serialize(request)
        
        # 요청 처리
        serialized_response = self.server_proxy.handle_request(serialized_request)
        
        # 응답 역직렬화
        response = Serializer.deserialize(serialized_response)
        
        # 응답 확인
        self.assertTrue(response.success)
        self.assertEqual(response.result, 8)  # 3 + 5 = 8
        self.assertEqual(response.request_id, request.message_id)
    
    def test_handle_request_method_not_found(self):
        """존재하지 않는 메서드 요청 테스트"""
        # 요청 생성
        request = Request(
            service_name="TestService",
            method_name="non_existent_method",
            parameters={}
        )
        
        # 요청 직렬화
        serialized_request = Serializer.serialize(request)
        
        # 요청 처리
        serialized_response = self.server_proxy.handle_request(serialized_request)
        
        # 응답 역직렬화
        response = Serializer.deserialize(serialized_response)
        
        # 응답 확인
        self.assertFalse(response.success)
        self.assertIn("메서드를 찾을 수 없음", response.error)
    
    def test_handle_request_method_error(self):
        """메서드 실행 중 오류 발생 테스트"""
        # 요청 생성
        request = Request(
            service_name="TestService",
            method_name="fail_method",
            parameters={}
        )
        
        # 요청 직렬화
        serialized_request = Serializer.serialize(request)
        
        # 요청 처리
        serialized_response = self.server_proxy.handle_request(serialized_request)
        
        # 응답 역직렬화
        response = Serializer.deserialize(serialized_response)
        
        # 응답 확인
        self.assertFalse(response.success)
        self.assertIn("요청 처리 중 오류", response.error)
        self.assertIn("의도적인 오류 발생", response.error)

class TestServer(unittest.TestCase):
    """서버 테스트"""
    
    def setUp(self):
        """테스트 사전 준비"""
        # 브로커 모의 구현
        self.mock_broker = MagicMock()
        self.mock_broker.register_service.return_value = True
        self.mock_broker.unregister_service.return_value = True
        
        # 테스트 서버 클래스 정의
        class TestServer(Server):
            def method1(self):
                return "method1 result"
                
            def method2(self, param):
                return f"method2 result: {param}"
        
        # 테스트 서버 생성
        self.server = TestServer(
            broker=self.mock_broker,
            service_name="TestService",
            description="Test service description"
        )
    
    def test_server_initialization(self):
        """서버 초기화 테스트"""
        # 브로커에 핸들러 등록 확인
        self.mock_broker.register_server_handler.assert_called_once()
        self.assertEqual(
            self.mock_broker.register_server_handler.call_args[0][0],
            self.server.server_id
        )
    
    def test_server_start_and_stop(self):
        """서버 시작 및 종료 테스트"""
        # 서버 시작
        result = self.server.start()
        self.assertTrue(result)
        
        # 브로커에 서비스 등록 확인
        self.mock_broker.register_service.assert_called_once()
        service_info = self.mock_broker.register_service.call_args[0][0]
        self.assertEqual(service_info.service_name, "TestService")
        self.assertEqual(service_info.description, "Test service description")
        self.assertEqual(service_info.server_id, self.server.server_id)
        self.assertListEqual(sorted(service_info.methods), ["method1", "method2"])
        
        # 서버 종료
        result = self.server.stop()
        self.assertTrue(result)
        
        # 브로커에서 서비스 등록 해제 확인
        self.mock_broker.unregister_service.assert_called_once_with(self.server.server_id)
        self.mock_broker.unregister_server_handler.assert_called_once_with(self.server.server_id)

if __name__ == "__main__":
    unittest.main() 