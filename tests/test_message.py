import unittest
from common.message import Message, Request, Response, ServiceInfo

class TestMessage(unittest.TestCase):
    """메시지 클래스 테스트"""
    
    def test_message_creation(self):
        """메시지 생성 테스트"""
        # 기본 메시지 (ID 자동 생성)
        msg1 = Message()
        self.assertIsNotNone(msg1.message_id)
        
        # ID 지정 메시지
        msg2 = Message(message_id="test_id")
        self.assertEqual(msg2.message_id, "test_id")
        
        # to_dict, from_dict 테스트
        msg_dict = msg2.to_dict()
        self.assertEqual(msg_dict["message_id"], "test_id")
        
        msg3 = Message.from_dict(msg_dict)
        self.assertEqual(msg3.message_id, "test_id")
    
    def test_request_creation(self):
        """요청 메시지 생성 테스트"""
        # 기본 요청
        req1 = Request("TestService", "test_method")
        self.assertEqual(req1.service_name, "TestService")
        self.assertEqual(req1.method_name, "test_method")
        self.assertEqual(req1.parameters, {})
        
        # 매개변수 및 ID 지정 요청
        req2 = Request(
            service_name="TestService",
            method_name="test_method",
            parameters={"arg1": 5, "arg2": "value"},
            message_id="req_id"
        )
        
        self.assertEqual(req2.service_name, "TestService")
        self.assertEqual(req2.method_name, "test_method")
        self.assertEqual(req2.parameters, {"arg1": 5, "arg2": "value"})
        self.assertEqual(req2.message_id, "req_id")
        
        # to_dict, from_dict 테스트
        req_dict = req2.to_dict()
        self.assertEqual(req_dict["service_name"], "TestService")
        self.assertEqual(req_dict["method_name"], "test_method")
        self.assertEqual(req_dict["parameters"], {"arg1": 5, "arg2": "value"})
        
        req3 = Request.from_dict(req_dict)
        self.assertEqual(req3.service_name, "TestService")
        self.assertEqual(req3.method_name, "test_method")
        self.assertEqual(req3.parameters, {"arg1": 5, "arg2": "value"})
    
    def test_response_creation(self):
        """응답 메시지 생성 테스트"""
        # 성공 응답
        resp1 = Response(result="test_result", request_id="orig_req_id")
        self.assertEqual(resp1.result, "test_result")
        self.assertEqual(resp1.request_id, "orig_req_id")
        self.assertIsNone(resp1.error)
        self.assertTrue(resp1.success)
        
        # 오류 응답
        resp2 = Response(
            error="test_error", 
            request_id="orig_req_id",
            message_id="resp_id"
        )
        
        self.assertEqual(resp2.error, "test_error")
        self.assertEqual(resp2.request_id, "orig_req_id")
        self.assertEqual(resp2.message_id, "resp_id")
        self.assertIsNone(resp2.result)
        self.assertFalse(resp2.success)
        
        # to_dict, from_dict 테스트
        resp_dict = resp2.to_dict()
        self.assertEqual(resp_dict["error"], "test_error")
        self.assertEqual(resp_dict["request_id"], "orig_req_id")
        self.assertFalse(resp_dict["success"])
        
        resp3 = Response.from_dict(resp_dict)
        self.assertEqual(resp3.error, "test_error")
        self.assertEqual(resp3.request_id, "orig_req_id")
        self.assertFalse(resp3.success)
    
    def test_service_info_creation(self):
        """서비스 정보 생성 테스트"""
        service_info = ServiceInfo(
            service_name="TestService",
            methods=["method1", "method2"],
            server_id="server_id",
            description="Test service description"
        )
        
        self.assertEqual(service_info.service_name, "TestService")
        self.assertEqual(service_info.methods, ["method1", "method2"])
        self.assertEqual(service_info.server_id, "server_id")
        self.assertEqual(service_info.description, "Test service description")
        
        # to_dict, from_dict 테스트
        si_dict = service_info.to_dict()
        self.assertEqual(si_dict["service_name"], "TestService")
        self.assertEqual(si_dict["methods"], ["method1", "method2"])
        
        si2 = ServiceInfo.from_dict(si_dict)
        self.assertEqual(si2.service_name, "TestService")
        self.assertEqual(si2.methods, ["method1", "method2"])

if __name__ == "__main__":
    unittest.main() 