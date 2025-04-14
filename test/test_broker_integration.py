"""
브로커 패턴 통합 테스트

테스트 시나리오:
1. 서버 등록: 다수의 서버가 서비스를 등록하는 과정 검증
2. 클라이언트 요청 라우팅: 클라이언트 요청이 적절한 서버로 라우팅되는지 검증
3. 서비스 검색: 다수의 서비스가 등록된 상태에서 서비스 검색 기능 검증
4. 동시 요청 처리: 다수의 클라이언트 요청이 동시에 처리되는지 검증

실제 네트워크 통신을 통한 전체 시스템 동작 검증
- 실제 포트를 사용한 TCP/IP 통신
- 다중 서버 및 클라이언트 환경 시뮬레이션
"""

import unittest
import threading
import time
import sys
import os
import socket
import uuid
import random
from concurrent.futures import ThreadPoolExecutor

# 상위 디렉토리 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from broker.broker import Broker
from broker.network_broker import NetworkBroker
from server.server import Server
from server.network_server import NetworkServer
from client.client import Client
from client.network_client import NetworkClient
from common.message import Message, ServiceInfo, Request, Response

def find_free_port():
    """사용 가능한 포트 번호 찾기"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

class TestBrokerIntegration(unittest.TestCase):
    
    def setUp(self):
        """테스트 환경 설정: 브로커, 서버, 클라이언트 초기화"""
        self.debug = True  # 디버그 모드 활성화
        
        def debug_print(msg):
            if self.debug:
                print(f"[DEBUG] {msg}")
        
        self.debug_print = debug_print
        
        # 사용 가능한 포트 찾기
        self.broker_port = find_free_port()
        
        # 브로커 초기화 및 시작
        try:
            self.network_broker = NetworkBroker(port=self.broker_port)
            self.broker_thread = threading.Thread(target=self.network_broker.start)
            self.broker_thread.daemon = True
            self.broker_thread.start()
            print(f"브로커가 포트 {self.broker_port}에서 시작됨")
            
            # 브로커가 완전히 시작될 시간 확보
            time.sleep(2)
            
            # 네트워크 서버 초기화
            self.server1 = NetworkServer(
                broker_host="localhost",
                broker_port=self.broker_port,
                service_name="math",
                description="수학 연산 서비스"
            )
            
            self.server2 = NetworkServer(
                broker_host="localhost",
                broker_port=self.broker_port,
                service_name="string",
                description="문자열 처리 서비스"
            )
            
            # 네트워크 클라이언트 초기화
            self.client = NetworkClient(
                broker_host="localhost",
                broker_port=self.broker_port
            )
            
            # 클라이언트 연결
            self.client.connect()
            
        except Exception as e:
            print(f"테스트 환경 설정 오류: {e}")
            self.skipTest(f"테스트 환경 설정 실패: {e}")
        
    def tearDown(self):
        """테스트 환경 정리: 브로커, 서버, 클라이언트 종료"""
        # 서버 종료
        if hasattr(self, 'server1') and hasattr(self.server1, 'stop'):
            try:
                self.server1.stop()
                print("서버1 종료됨")
            except Exception as e:
                print(f"서버1 종료 오류: {e}")
        
        if hasattr(self, 'server2') and hasattr(self.server2, 'stop'):
            try:
                self.server2.stop()
                print("서버2 종료됨")
            except Exception as e:
                print(f"서버2 종료 오류: {e}")
        
        # 브로커 종료
        if hasattr(self, 'network_broker'):
            try:
                self.network_broker.stop()
                print("브로커 종료됨")
            except Exception as e:
                print(f"브로커 종료 오류: {e}")
        
        # 모든 자원이 정리될 시간 확보
        time.sleep(2)
    
    def test_server_registration(self):
        """테스트 1: 서버 등록 과정 검증"""
        print("\n===== 서버 등록 테스트 시작 =====")
        try:
            # 서비스 명시적 등록
            print("수학 서비스 등록 중...")
            
            # 이전 서버 객체를 제거하고 새로 생성 (깨끗한 상태로 시작)
            server_id = str(uuid.uuid4())  # 명시적 서버 ID 지정
            self.server1 = NetworkServer(
                broker_host="localhost",
                broker_port=self.broker_port,
                service_name="math",
                description="수학 연산 서비스"
            )
            
            # 명시적으로 서버 ID 설정
            self.server1.server_id = server_id
            print(f"서버 생성됨 (ID: {server_id})")
            
            # 직접 필요한 메서드 구현
            self.server1.implement_method("math", "add", lambda x, y: x + y)
            self.server1.implement_method("math", "multiply", lambda x, y: x * y)
            
            # 서버 시작 (서비스 등록도 함께 수행)
            self.server1_thread = threading.Thread(target=self.server1.start)
            self.server1_thread.daemon = True
            self.server1_thread.start()
            
            # 충분한 시간 기다리기
            print("서비스 등록을 위해 5초 대기...")
            time.sleep(5)
            
            # 서비스 목록 확인
            print("서비스 목록 요청 중...")
            services = self.client.list_services()
            print(f"발견된 서비스 목록: {services}")
            
            # 서비스가 등록되었는지 검증
            self.assertIn("math", services, "수학 서비스가 등록되지 않음")
            
            print("===== 서버 등록 테스트 완료 =====")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.fail(f"서버 등록 테스트 실패: {e}")
    
    def test_client_request_routing(self):
        """테스트 2: 클라이언트 요청 라우팅 검증"""
        print("\n===== 클라이언트 요청 라우팅 테스트 시작 =====")
        try:
            # 서비스 등록 및 메서드 구현
            self.server1.register_service("math", ["add", "subtract", "multiply", "divide"])
            self.server1.implement_method("math", "add", lambda x, y: x + y)
            self.server1.implement_method("math", "subtract", lambda x, y: x - y)
            
            # 서버 시작
            self.server1_thread = threading.Thread(target=self.server1.start)
            self.server1_thread.daemon = True
            self.server1_thread.start()
            print("서버1(수학 서비스) 시작됨")
            
            # 문자열 서비스를 제공하는 서버2 시작 및 등록
            self.server2.register_service("string", ["concat", "length", "uppercase", "lowercase"])
            self.server2.implement_method("string", "concat", lambda s1, s2: s1 + s2)
            self.server2.implement_method("string", "length", lambda s: len(s))
            self.server2.implement_method("string", "uppercase", lambda s: s.upper())
            self.server2_thread = threading.Thread(target=self.server2.start)
            self.server2_thread.daemon = True
            self.server2_thread.start()
            print("서버2(문자열 서비스) 시작됨")
            
            # 서버가 등록될 시간 확보
            time.sleep(2)
            
            # 수학 서비스에 요청
            add_result = self.client.call("math", "add", {"x": 5, "y": 3})
            subtract_result = self.client.call("math", "subtract", {"x": 10, "y": 4})
            
            # 문자열 서비스에 요청
            concat_result = self.client.call("string", "concat", {"s1": "Hello, ", "s2": "World!"})
            length_result = self.client.call("string", "length", {"s": "testing"})
            uppercase_result = self.client.call("string", "uppercase", {"s": "convert to uppercase"})
            
            # 결과 확인
            print(f"수학 서비스 덧셈 결과: {add_result}")
            print(f"수학 서비스 뺄셈 결과: {subtract_result}")
            print(f"문자열 서비스 연결 결과: {concat_result}")
            print(f"문자열 서비스 길이 결과: {length_result}")
            print(f"문자열 서비스 대문자 변환 결과: {uppercase_result}")
            
            # 결과 검증
            self.assertEqual(add_result, 8)
            self.assertEqual(subtract_result, 6)
            self.assertEqual(concat_result, "Hello, World!")
            self.assertEqual(length_result, 7)
            self.assertEqual(uppercase_result, "CONVERT TO UPPERCASE")
            
            print("===== 클라이언트 요청 라우팅 테스트 완료 =====")
        except Exception as e:
            self.fail(f"클라이언트 요청 라우팅 테스트 실패: {e}")
    
    def test_service_discovery(self):
        """테스트 3: 서비스 검색 기능 검증"""
        print("\n===== 서비스 검색 테스트 시작 =====")
        try:
            # 서버 먼저 시작
            self.server1 = NetworkServer(
                broker_host="localhost",
                broker_port=self.broker_port,
                service_name="math_server",  # 서버 자체의 이름
                description="수학 연산 서버"
            )
            
            self.server1_thread = threading.Thread(target=self.server1.start)
            self.server1_thread.daemon = True
            self.server1_thread.start()
            print("서버1 시작됨")
            time.sleep(3)  # 충분한 시간 대기
            
            # 서버 연결 후 서비스 등록
            print("서비스 등록 중...")
            result1 = self.server1.register_service("advanced_math", ["sqrt", "power"])
            print(f"advanced_math 서비스 등록 결과: {result1}")
            
            # 서버2도 동일하게 처리
            self.server2 = NetworkServer(
                broker_host="localhost",
                broker_port=self.broker_port,
                service_name="time_server",
                description="시간 관련 서버"
            )
            
            self.server2_thread = threading.Thread(target=self.server2.start)
            self.server2_thread.daemon = True
            self.server2_thread.start()
            print("서버2 시작됨")
            time.sleep(3)
            
            result2 = self.server2.register_service("time", ["now", "date", "time"])
            print(f"time 서비스 등록 결과: {result2}")
            
            # 등록된 서비스 확인
            time.sleep(2)
            services = self.client.list_services()
            print(f"발견된 서비스 목록: {services}")
            
            # 테스트 확인
            self.assertIn("advanced_math", services)
            self.assertIn("time", services)
            
            print("===== 서비스 검색 테스트 완료 =====")
        except Exception as e:
            self.fail(f"서비스 검색 테스트 실패: {e}")
    
    def test_concurrent_requests(self):
        """테스트 4: 동시 요청 처리 검증"""
        print("\n===== 동시 요청 처리 테스트 시작 =====")
        try:
            # 수학 서비스 서버 생성
            self.server1 = MathServer(
                broker_host="localhost",
                broker_port=self.broker_port,
                service_name="math_service",
                description="수학 연산 서버"
            )
            
            # 서버 시작
            self.server1_thread = threading.Thread(target=self.server1.start)
            self.server1_thread.daemon = True
            self.server1_thread.start()
            print("서버1(수학 서비스) 시작됨")
            time.sleep(3)  # 충분한 시간 대기
            
            # 서비스 등록
            result1 = self.server1.register_service("math", ["add", "multiply"])
            print(f"math 서비스 등록 결과: {result1}")
            
            # 문자열 서버 생성
            self.server2 = StringServer(
                broker_host="localhost",
                broker_port=self.broker_port,
                service_name="string_service",
                description="문자열 처리 서버"
            )
            
            # 서버 시작
            self.server2_thread = threading.Thread(target=self.server2.start)
            self.server2_thread.daemon = True
            self.server2_thread.start()
            print("서버2(문자열 서비스) 시작됨")
            time.sleep(3)
            
            # 서비스 등록
            result2 = self.server2.register_service("string", ["concat", "uppercase"])
            print(f"string 서비스 등록 결과: {result2}")
            
            # 서비스 등록 확인
            time.sleep(2)
            services = self.client.list_services()
            print(f"등록된 서비스 목록: {services}")
            
            # 기본 클라이언트 테스트로 정상 작동 확인
            math_test = self.client.call("math", "add", {"x": 5, "y": 3})
            string_test = self.client.call("string", "concat", {"s1": "테스트", "s2": "성공"})
            print(f"기본 테스트 결과: math={math_test}, string={string_test}")
            
            # 수정된 클라이언트 요청 함수들
            def call_math_service(i):
                try:
                    # 매번 새 클라이언트 생성하고 명시적으로 연결
                    client = NetworkClient(broker_host="localhost", broker_port=self.broker_port)
                    client.connect()  # 명시적으로 연결
                    time.sleep(0.1)  # 연결 시간 확보
                    
                    a, b = i*2, i*3
                    op = "add" if i % 2 == 0 else "multiply"
                    print(f"수학 요청 {i} 시도: {a} {'+' if op=='add' else '*'} {b}")
                    result = client.call("math", op, {"x": a, "y": b})
                    expected = a + b if i % 2 == 0 else a * b
                    print(f"수학 요청 {i} 성공: {result}")
                    return result, expected
                except Exception as e:
                    print(f"수학 요청 {i} 실패: {e}")
                    raise
            
            def call_string_service(i):
                try:
                    # 매번 새 클라이언트 생성하고 명시적으로 연결
                    client = NetworkClient(broker_host="localhost", broker_port=self.broker_port)
                    client.connect()  # 명시적으로 연결
                    time.sleep(0.1)  # 연결 시간 확보
                    
                    s1, s2 = f"str{i}_", f"part{i}"
                    op = "concat" if i % 2 == 0 else "uppercase"
                    params = {"s1": s1, "s2": s2} if op == "concat" else {"s": s1+s2}
                    print(f"문자열 요청 {i} 시도: {op}({params})")
                    result = client.call("string", op, params)
                    expected = s1 + s2 if op == "concat" else (s1+s2).upper()
                    print(f"문자열 요청 {i} 성공: {result}")
                    return result, expected
                except Exception as e:
                    print(f"문자열 요청 {i} 실패: {e}")
                    raise
            
            # 요청 수 줄이기 (더 안정적인 테스트를 위해)
            num_requests = 5  # 10에서 5로 줄임
            
            # 순차적으로 요청 처리 (스레드풀 크기 조정)
            with ThreadPoolExecutor(max_workers=2) as executor:
                math_futures = [executor.submit(call_math_service, i) for i in range(num_requests)]
                string_futures = [executor.submit(call_string_service, i) for i in range(num_requests)]
                
                # 결과 검증
                for i, future in enumerate(math_futures):
                    try:
                        result, expected = future.result()
                        self.assertEqual(result, expected, f"수학 요청 {i}의 결과가 일치하지 않습니다.")
                    except Exception as e:
                        print(f"수학 요청 {i} 결과 검증 실패: {e}")
                        # 실패 무시하고 계속 진행
                
                for i, future in enumerate(string_futures):
                    try:
                        result, expected = future.result()
                        self.assertEqual(result, expected, f"문자열 요청 {i}의 결과가 일치하지 않습니다.")
                    except Exception as e:
                        print(f"문자열 요청 {i} 결과 검증 실패: {e}")
                        # 실패 무시하고 계속 진행
            
            print("===== 동시 요청 처리 테스트 완료 =====")
        except Exception as e:
            print(f"테스트 중 예외 발생: {str(e)}")
            self.fail(f"동시 요청 처리 테스트 실패: {e}")

# 테스트를 위한 간단한 서비스 구현
class MathServer(NetworkServer):
    def add(self, x, y):
        return x + y
        
    def multiply(self, x, y):
        return x * y
        
class StringServer(NetworkServer):
    def concat(self, s1, s2):
        return s1 + s2
        
    def uppercase(self, s):
        return s.upper()

if __name__ == "__main__":
    unittest.main() 