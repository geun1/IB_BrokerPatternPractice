import unittest
from broker.broker import Broker
from server.server import Server
from client.client import Client

class EchoServer(Server):
    """통합 테스트용 에코 서버"""
    
    def __init__(self, broker):
        super().__init__(
            broker=broker,
            service_name="Echo",
            description="간단한 에코 서비스"
        )
    
    def echo(self, message):
        """메시지를 그대로 반환"""
        return message
    
    def reverse(self, message):
        """메시지를 뒤집어서 반환"""
        return message[::-1]
    
    def upper(self, message):
        """메시지를 대문자로 변환"""
        return message.upper()
    
    def concat(self, messages):
        """여러 메시지를 연결"""
        return "".join(messages)

class MathServer(Server):
    """통합 테스트용 수학 서버"""
    
    def __init__(self, broker):
        super().__init__(
            broker=broker,
            service_name="Math",
            description="기본 수학 연산 서비스"
        )
    
    def add(self, a, b):
        """덧셈"""
        return a + b
    
    def subtract(self, a, b):
        """뺄셈"""
        return a - b
    
    def multiply(self, a, b):
        """곱셈"""
        return a * b
    
    def divide(self, a, b):
        """나눗셈"""
        if b == 0:
            raise ValueError("0으로 나눌 수 없습니다")
        return a / b

class TestIntegration(unittest.TestCase):
    """전체 시스템 통합 테스트"""
    
    def setUp(self):
        """테스트 사전 준비"""
        # 브로커 생성
        self.broker = Broker()
        
        # 서버 생성 및 시작
        self.echo_server = EchoServer(self.broker)
        self.math_server = MathServer(self.broker)
        
        self.echo_server.start()
        self.math_server.start()
        
        # 클라이언트 생성
        self.client = Client(self.broker)
    
    def tearDown(self):
        """테스트 정리"""
        # 서버 종료
        self.echo_server.stop()
        self.math_server.stop()
    
    def test_service_discovery(self):
        """서비스 탐색 테스트"""
        # 사용 가능한 서비스 목록 확인
        services = self.client.list_services()
        self.assertEqual(len(services), 2)
        self.assertIn("Echo", services)
        self.assertIn("Math", services)
    
    def test_echo_service(self):
        """에코 서비스 테스트"""
        # 에코 서비스 프록시 가져오기
        echo_service = self.client.get_service("Echo")
        self.assertIsNotNone(echo_service)
        
        # echo 메서드 테스트
        result = echo_service.echo(message="Hello, World!")
        self.assertEqual(result, "Hello, World!")
        
        # reverse 메서드 테스트
        result = echo_service.reverse(message="Hello, World!")
        self.assertEqual(result, "!dlroW ,olleH")
        
        # upper 메서드 테스트
        result = echo_service.upper(message="Hello, World!")
        self.assertEqual(result, "HELLO, WORLD!")
        
        # concat 메서드 테스트
        result = echo_service.concat(messages=["Hello", ", ", "World", "!"])
        self.assertEqual(result, "Hello, World!")
    
    def test_math_service(self):
        """수학 서비스 테스트"""
        # 수학 서비스 프록시 가져오기
        math_service = self.client.get_service("Math")
        self.assertIsNotNone(math_service)
        
        # add 메서드 테스트
        result = math_service.add(a=5, b=3)
        self.assertEqual(result, 8)
        
        # subtract 메서드 테스트
        result = math_service.subtract(a=10, b=4)
        self.assertEqual(result, 6)
        
        # multiply 메서드 테스트
        result = math_service.multiply(a=6, b=7)
        self.assertEqual(result, 42)
        
        # divide 메서드 테스트
        result = math_service.divide(a=15, b=3)
        self.assertEqual(result, 5)
        
        # 오류 테스트 (0으로 나누기)
        with self.assertRaises(Exception) as context:
            math_service.divide(a=10, b=0)
        self.assertIn("0으로 나눌 수 없습니다", str(context.exception))
    
    def test_unknown_service(self):
        """존재하지 않는 서비스 테스트"""
        # 없는 서비스 프록시 시도
        unknown_service = self.client.get_service("UnknownService")
        self.assertIsNone(unknown_service)

if __name__ == "__main__":
    unittest.main() 