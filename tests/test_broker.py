import unittest
from broker.broker import Broker, ServiceRepository
from common.message import ServiceInfo, Request, Response

class TestServiceRepository(unittest.TestCase):
    """서비스 레포지토리 테스트"""
    
    def setUp(self):
        """테스트 사전 준비"""
        self.repo = ServiceRepository()
        
        # 테스트 서비스 정보
        self.service_info1 = ServiceInfo(
            service_name="TestService1",
            methods=["method1", "method2"],
            server_id="server1",
            description="Test service 1"
        )
        
        self.service_info2 = ServiceInfo(
            service_name="TestService2",
            methods=["method3", "method4"],
            server_id="server2",
            description="Test service 2"
        )
        
        self.service_info3 = ServiceInfo(
            service_name="TestService1",  # 같은 서비스 이름, 다른 서버
            methods=["method1", "method5"],
            server_id="server3",
            description="Test service 1 - another instance"
        )
    
    def test_register_service(self):
        """서비스 등록 테스트"""
        # 첫 번째 서비스 등록
        result = self.repo.register_service(self.service_info1)
        self.assertTrue(result)
        self.assertEqual(len(self.repo.services), 1)
        self.assertEqual(len(self.repo.services["TestService1"]), 1)
        
        # 두 번째 서비스 등록 (다른 서비스 이름)
        result = self.repo.register_service(self.service_info2)
        self.assertTrue(result)
        self.assertEqual(len(self.repo.services), 2)
        self.assertEqual(len(self.repo.services["TestService2"]), 1)
        
        # 세 번째 서비스 등록 (같은 서비스 이름, 다른 서버)
        result = self.repo.register_service(self.service_info3)
        self.assertTrue(result)
        self.assertEqual(len(self.repo.services), 2)
        self.assertEqual(len(self.repo.services["TestService1"]), 2)
    
    def test_find_service(self):
        """서비스 찾기 테스트"""
        # 서비스 등록
        self.repo.register_service(self.service_info1)
        self.repo.register_service(self.service_info2)
        self.repo.register_service(self.service_info3)
        
        # 존재하는 서비스 찾기
        service = self.repo.find_service("TestService1")
        self.assertIsNotNone(service)
        self.assertEqual(service.service_name, "TestService1")
        
        # 존재하지 않는 서비스 찾기
        service = self.repo.find_service("NonExistentService")
        self.assertIsNone(service)
    
    def test_unregister_service(self):
        """서비스 등록 해제 테스트"""
        # 서비스 등록
        self.repo.register_service(self.service_info1)
        self.repo.register_service(self.service_info2)
        self.repo.register_service(self.service_info3)
        
        # 특정 서비스만 등록 해제
        result = self.repo.unregister_service("server1", "TestService1")
        self.assertTrue(result)
        self.assertEqual(len(self.repo.services["TestService1"]), 1)  # 하나는 남아 있어야 함
        
        # 모든 서비스 등록 해제
        result = self.repo.unregister_service("server3")
        self.assertTrue(result)
        self.assertNotIn("TestService1", self.repo.services)  # 해당 서비스가 완전히 삭제됨
        self.assertEqual(len(self.repo.services), 1)  # TestService2만 남아있음
    
    def test_list_services(self):
        """서비스 목록 테스트"""
        # 서비스 등록
        self.repo.register_service(self.service_info1)
        self.repo.register_service(self.service_info2)
        
        # 서비스 목록 확인
        services = self.repo.list_services()
        self.assertEqual(len(services), 2)
        self.assertIn("TestService1", services)
        self.assertIn("TestService2", services)

class TestBroker(unittest.TestCase):
    """브로커 테스트"""
    
    def setUp(self):
        """테스트 사전 준비"""
        self.broker = Broker()
        
        # 테스트 서비스 정보
        self.service_info = ServiceInfo(
            service_name="TestService",
            methods=["echo"],
            server_id="server1",
            description="Test echo service"
        )
        
        # 테스트 요청 핸들러
        def test_handler(serialized_request):
            from common.serializer import Serializer
            request = Serializer.deserialize(serialized_request)
            
            if request.method_name == "echo":
                response = Response(
                    result=request.parameters.get("message", ""),
                    request_id=request.message_id
                )
            else:
                response = Response(
                    error=f"Unknown method: {request.method_name}",
                    request_id=request.message_id
                )
                
            return Serializer.serialize(response)
            
        self.test_handler = test_handler
    
    def test_register_service_and_handler(self):
        """서비스 및 핸들러 등록 테스트"""
        # 서비스 및 핸들러 등록
        self.broker.register_service(self.service_info)
        self.broker.register_server_handler("server1", self.test_handler)
        
        # 등록 확인
        services = self.broker.list_services()
        self.assertIn("TestService", services)
        
        # 서버 ID 확인 (register_server_handler 실행 여부 검증)
        self.assertIn("server1", self.broker.server_handlers)
    
    def test_forward_request(self):
        """요청 전달 테스트"""
        # 서비스 및 핸들러 등록
        self.broker.register_service(self.service_info)
        self.broker.register_server_handler("server1", self.test_handler)
        
        # 요청 생성 및 전달
        request = Request(
            service_name="TestService",
            method_name="echo",
            parameters={"message": "Hello, Broker!"}
        )
        
        response = self.broker.forward_request(request)
        
        # 응답 확인
        self.assertTrue(response.success)
        self.assertEqual(response.result, "Hello, Broker!")
        self.assertEqual(response.request_id, request.message_id)
    
    def test_forward_request_unknown_service(self):
        """알 수 없는 서비스 요청 테스트"""
        # 요청 생성 및 전달 (서비스 등록 없이)
        request = Request(
            service_name="UnknownService",
            method_name="echo",
            parameters={"message": "Hello, Broker!"}
        )
        
        response = self.broker.forward_request(request)
        
        # 응답 확인 (오류 발생)
        self.assertFalse(response.success)
        self.assertIn("서비스를 찾을 수 없음", response.error)
    
    def test_unregister_service_and_handler(self):
        """서비스 및 핸들러 등록 해제 테스트"""
        # 서비스 및 핸들러 등록
        self.broker.register_service(self.service_info)
        self.broker.register_server_handler("server1", self.test_handler)
        
        # 등록 해제
        self.broker.unregister_service("server1")
        self.broker.unregister_server_handler("server1")
        
        # 등록 해제 확인
        services = self.broker.list_services()
        self.assertNotIn("TestService", services)
        self.assertNotIn("server1", self.broker.server_handlers)

if __name__ == "__main__":
    unittest.main() 