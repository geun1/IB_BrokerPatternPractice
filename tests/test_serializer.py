import unittest
from common.serializer import Serializer
from common.message import Message, Request, Response, ServiceInfo

class TestSerializer(unittest.TestCase):
    """직렬화/역직렬화 테스트"""
    
    def test_serialize_primitive(self):
        """기본 데이터 타입 직렬화 테스트"""
        # 정수
        self.assertEqual(Serializer.deserialize(Serializer.serialize(42)), 42)
        # 실수
        self.assertEqual(Serializer.deserialize(Serializer.serialize(3.14)), 3.14)
        # 문자열
        self.assertEqual(Serializer.deserialize(Serializer.serialize("test")), "test")
        # 리스트
        self.assertEqual(Serializer.deserialize(Serializer.serialize([1, 2, 3])), [1, 2, 3])
        # 딕셔너리
        self.assertEqual(Serializer.deserialize(Serializer.serialize({"a": 1, "b": 2})), {"a": 1, "b": 2})
    
    def test_serialize_message(self):
        """메시지 객체 직렬화 테스트"""
        # Message 객체
        msg = Message(message_id="test_id")
        serialized = Serializer.serialize(msg)
        deserialized = Serializer.deserialize(serialized, {"Message": Message})
        
        self.assertEqual(deserialized.message_id, msg.message_id)
    
    def test_serialize_request(self):
        """요청 객체 직렬화 테스트"""
        req = Request(
            service_name="TestService",
            method_name="test_method",
            parameters={"arg1": 5, "arg2": "value"},
            message_id="req_id"
        )
        
        serialized = Serializer.serialize(req)
        deserialized = Serializer.deserialize(serialized, {"Request": Request})
        
        self.assertEqual(deserialized.service_name, req.service_name)
        self.assertEqual(deserialized.method_name, req.method_name)
        self.assertEqual(deserialized.parameters, req.parameters)
        self.assertEqual(deserialized.message_id, req.message_id)
    
    def test_serialize_response(self):
        """응답 객체 직렬화 테스트"""
        resp = Response(
            result="test_result",
            request_id="orig_req_id",
            message_id="resp_id"
        )
        
        serialized = Serializer.serialize(resp)
        deserialized = Serializer.deserialize(serialized, {"Response": Response})
        
        self.assertEqual(deserialized.result, resp.result)
        self.assertEqual(deserialized.request_id, resp.request_id)
        self.assertEqual(deserialized.message_id, resp.message_id)
        self.assertTrue(deserialized.success)
    
    def test_serialize_error_response(self):
        """오류 응답 직렬화 테스트"""
        err_resp = Response(
            error="test_error",
            request_id="orig_req_id",
            message_id="resp_id"
        )
        
        serialized = Serializer.serialize(err_resp)
        deserialized = Serializer.deserialize(serialized, {"Response": Response})
        
        self.assertEqual(deserialized.error, err_resp.error)
        self.assertEqual(deserialized.request_id, err_resp.request_id)
        self.assertEqual(deserialized.message_id, err_resp.message_id)
        self.assertFalse(deserialized.success)
    
    def test_serialize_service_info(self):
        """서비스 정보 직렬화 테스트"""
        service_info = ServiceInfo(
            service_name="TestService",
            methods=["method1", "method2"],
            server_id="server_id",
            description="Test service description"
        )
        
        serialized = Serializer.serialize(service_info)
        deserialized = Serializer.deserialize(serialized, {"ServiceInfo": ServiceInfo})
        
        self.assertEqual(deserialized.service_name, service_info.service_name)
        self.assertEqual(deserialized.methods, service_info.methods)
        self.assertEqual(deserialized.server_id, service_info.server_id)
        self.assertEqual(deserialized.description, service_info.description)

if __name__ == "__main__":
    unittest.main() 