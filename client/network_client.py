"""
네트워크 기반 클라이언트 구현체

주요 기능:
1. 브로커 연결: 네트워크를 통해 브로커에 연결
2. 서비스 검색: 사용 가능한 서비스 목록 조회
3. 서비스 호출: 원격 서비스 메서드 호출
4. 응답 처리: 서버 응답 수신 및 처리

구현 세부사항:
- NetworkTransport를 통한 브로커와의 통신
- 동기식 요청-응답 모델
- 요청 타임아웃 처리
- 동적 프록시 메서드 생성: 서비스.메서드() 형태의 호출 지원
"""

import json
import threading
from typing import Dict, List, Optional
from client.client_proxy import ClientProxy
from common.message import Request, Response
from network.transport import NetworkTransport
import traceback
import uuid

class NetworkClientProxy(ClientProxy):
    """
    네트워크 환경에서 동작하는 클라이언트 프록시
    """
    
    def __init__(self, transport, service_name):
        """
        네트워크 클라이언트 프록시 초기화
        
        Args:
            transport: 네트워크 트랜스포트
            service_name: 사용할 서비스 이름
        """
        self.transport = transport
        self.service_name = service_name
        self.response_events = {}
        self.responses = {}
        
    def call_method(self, method_name, *args, **kwargs):
        """
        서비스 메서드 호출
        
        Args:
            method_name: 호출할 메서드 이름
            *args: 위치 인자
            **kwargs: 키워드 인자
            
        Returns:
            메서드 호출 결과
        """
        # 요청 ID 생성
        request_id = str(uuid.uuid4())
        
        # 이벤트 및 응답 저장소 초기화
        self.response_events[request_id] = threading.Event()
        self.responses[request_id] = None
        
        # 요청 생성 및 전송
        request = Request(
            message_id=request_id,
            service_name=self.service_name,
            method_name=method_name,
            parameters=kwargs if kwargs else args[0] if args else {}
        )
        
        print(f"[클라이언트] 요청 전송: {self.service_name}.{method_name}() (요청 ID: {request_id})")
        
        # 요청 전송
        self.transport.send_message({
            'type': 'forward_request',
            'payload': {
                'request': request.to_dict()
            }
        })
        
        # 응답 대기
        print(f"[클라이언트] 응답 대기 중: {self.service_name}.{method_name}() (요청 ID: {request_id})")
        if not self.response_events[request_id].wait(timeout=10.0):  # 타임아웃 시간 증가 (5초 -> 10초)
            print(f"[클라이언트] 타임아웃 발생: {self.service_name}.{method_name}() (요청 ID: {request_id})")
            del self.response_events[request_id]
            raise TimeoutError(f"서비스 호출 타임아웃: {self.service_name}.{method_name}")
        
        # 응답 반환
        response = self.responses[request_id]
        del self.responses[request_id]
        del self.response_events[request_id]
        
        # 오류 확인
        if response.error:
            raise Exception(f"서비스 호출 오류: {response.error}")
        
        return response.result
        
    def handle_response(self, response):
        """
        서버로부터 받은 응답 처리
        
        Args:
            response: 응답 객체
        """
        request_id = response.request_id
        
        # 응답 저장 및 이벤트 설정
        if request_id in self.response_events:
            self.responses[request_id] = response
            self.response_events[request_id].set()

    def __getattr__(self, name):
        """
        동적 메서드 호출
        
        Args:
            name: 호출할 메서드 이름
        
        Returns:
            메서드 호출 래퍼 함수
        """
        if name.startswith('_'):  # 내부 메서드는 기본 동작 유지
            raise AttributeError(f"'{self.__class__.__name__}' 객체에 '{name}' 속성이 없습니다")
        
        # 동적 메서드 래퍼 생성
        def method_wrapper(*args, **kwargs):
            # 실제 메서드 호출 처리
            return self.call_method(name, *args, **kwargs)
        
        return method_wrapper

    def _handle_forward_response(self, payload, client_sock):
        """요청 전달 응답 처리"""
        try:
            # 응답 디버깅
            print(f"[클라이언트] 응답 수신: {payload}")
            
            # 응답 파싱
            response_dict = payload.get('response')
            if not response_dict:
                print(f"[클라이언트] 경고: 응답에 'response' 필드가 없습니다: {payload}")
                return None
                
            response = Response.from_dict(response_dict)
            
            # 요청 ID 확인
            request_id = response.request_id
            print(f"[클라이언트] 응답 처리 중: (요청 ID: {request_id})")
            
            # 해당 요청의 프록시가 있는지 확인
            for service_name, proxy in self.proxies.items():
                if hasattr(proxy, 'response_events') and request_id in proxy.response_events:
                    # 응답 저장 및 이벤트 설정
                    proxy.responses[request_id] = response
                    proxy.response_events[request_id].set()
                    print(f"[클라이언트] 응답 이벤트 설정됨: (요청 ID: {request_id})")
                    break
            
            return None  # 응답 불필요
        except Exception as e:
            print(f"응답 처리 중 오류: {str(e)}")
            traceback.print_exc()
            return None

class NetworkClient:
    """
    네트워크를 통해 브로커에 연결되는 클라이언트
    """
    
    def __init__(self, broker_host='localhost', broker_port=5000):
        """
        네트워크 클라이언트 초기화
        
        Args:
            broker_host: 브로커 호스트
            broker_port: 브로커 포트
        """
        self.transport = NetworkTransport(broker_host, broker_port)
        self.proxies = {}
        self.services_cache = None
        self.response_event = threading.Event()
        self.response_data = None
        
    def connect(self):
        """
        브로커 서버에 연결
        """
        # 브로커 서버에 연결
        self.transport.connect_to_server()
        
        # 메시지 핸들러 등록
        self.transport.register_handler('forward_request_response', self._handle_forward_response)
        self.transport.register_handler('list_services_response', self._handle_list_services_response)
        
        print("브로커 서버에 연결되었습니다.")
        
    def disconnect(self):
        """
        브로커 서버 연결 종료
        """
        self.transport.stop()
        print("브로커 서버 연결이 종료되었습니다.")
        
    def get_service(self, service_name):
        """
        서비스 프록시 가져오기
        
        Args:
            service_name: 사용할 서비스 이름
            
        Returns:
            서비스 프록시 (서비스가 없으면 None)
        """
        # 서비스가 존재하는지 확인
        available_services = self.list_services()
        if service_name not in available_services:
            return None
        
        # 프록시가 이미 생성되었는지 확인
        if service_name not in self.proxies:
            self.proxies[service_name] = NetworkClientProxy(self.transport, service_name)
            
        return self.proxies[service_name]
        
    def list_services(self):
        """
        서비스 목록 조회
        
        Returns:
            서비스 목록 (서비스 이름 리스트)
        """
        # 이벤트 초기화
        self.response_event.clear()
        self.response_data = None
        
        # 브로커에 서비스 목록 요청 메시지 전송
        message = {
            'type': 'list_services',
            'payload': {}
        }
        
        print("서비스 목록 요청 메시지 전송...")
        self.transport.send_message(message)
        
        # 응답 대기
        if not self.response_event.wait(timeout=5.0):
            print("서비스 목록 요청 타임아웃")
            return []
        
        # 핵심 수정: 응답 데이터에서 services 항목 올바르게 추출
        if self.response_data and 'services' in self.response_data:
            services = self.response_data['services']
            print(f"직접 접근 서비스 목록: {services}")
            return services
        
        # 중첩 구조 확인
        if (self.response_data and 'payload' in self.response_data and 
            'services' in self.response_data['payload']):
            services = self.response_data['payload']['services']
            print(f"페이로드 접근 서비스 목록: {services}")
            return services
        
        print(f"서비스 목록을 찾을 수 없음: {self.response_data}")
        return []
        
    def _handle_forward_response(self, payload, client_sock):
        """요청 전달 응답 처리"""
        try:
            # 응답 디버깅
            print(f"[클라이언트] 응답 수신: {payload}")
            
            # 응답 파싱
            response_dict = payload.get('response')
            if not response_dict:
                print(f"[클라이언트] 경고: 응답에 'response' 필드가 없습니다: {payload}")
                return None
                
            response = Response.from_dict(response_dict)
            
            # 요청 ID 확인
            request_id = response.request_id
            print(f"[클라이언트] 응답 처리 중: (요청 ID: {request_id})")
            
            # 해당 요청의 프록시가 있는지 확인
            for service_name, proxy in self.proxies.items():
                if hasattr(proxy, 'response_events') and request_id in proxy.response_events:
                    # 응답 저장 및 이벤트 설정
                    proxy.responses[request_id] = response
                    proxy.response_events[request_id].set()
                    print(f"[클라이언트] 응답 이벤트 설정됨: (요청 ID: {request_id})")
                    break
            
            return None  # 응답 불필요
        except Exception as e:
            print(f"응답 처리 중 오류: {str(e)}")
            traceback.print_exc()
            return None
        
    def _handle_list_services_response(self, payload, client_sock):
        """
        서비스 목록 응답 처리
        """
        print(f"서비스 목록 응답 수신: {payload}")
        
        # 전체 응답을 저장
        self.response_data = payload
        
        # 이벤트 설정
        self.response_event.set()
        
        return None  # 응답 불필요

    def call(self, service_name, method_name, parameters):
        """
        서비스 메서드 호출 (테스트 호환성을 위한 메서드)
        
        Args:
            service_name: 서비스 이름
            method_name: 메서드 이름
            parameters: 메서드 파라미터 (딕셔너리)
            
        Returns:
            메서드 호출 결과
        """
        # 서비스 프록시 가져오기
        service = self.get_service(service_name)
        if not service:
            raise Exception(f"서비스를 찾을 수 없음: {service_name}")
        
        # 동적 메서드 호출
        method = getattr(service, method_name)
        return method(**parameters) 