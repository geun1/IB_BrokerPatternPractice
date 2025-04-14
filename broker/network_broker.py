"""
네트워크 통신을 통한 브로커 구현체

주요 기능:
1. 소켓 통신: TCP/IP 소켓을 통한 클라이언트 및 서버 연결 처리
2. 메시지 직렬화/역직렬화: JSON 기반 메시지 처리
3. 서비스 레지스트리: 등록된 서비스와 서버 정보 유지
4. 동시성 처리: 다중 클라이언트 및 서버 연결 동시 처리
5. 요청-응답 매핑: 클라이언트 요청과 서버 응답 간의 매핑 관리

구현 세부사항:
- 멀티스레드 소켓 서버로 구현
- 각 클라이언트/서버 연결에 대한 별도 스레드 할당
- 메시지 타입에 따른 핸들러 등록 및 호출
"""

import uuid
import json
import threading
from typing import Dict, Any, List
from broker.broker import Broker
from common.message import Request, Response, ServiceInfo
from common.serializer import Serializer
from network.transport import NetworkTransport
import traceback
import socket

class NetworkBroker:
    """
    네트워크를 통한 분산 브로커 서비스
    """
    
    def __init__(self, host='localhost', port=5000):
        """
        네트워크 브로커 초기화
        
        Args:
            host: 호스트 주소
            port: 포트 번호
        """
        self.broker = Broker()  # 로컬 브로커 인스턴스
        self.transport = NetworkTransport(host, port)
        self.server_connections = {}  # 서버 ID -> 클라이언트 소켓
        self.request_connections = {}  # 요청 ID -> 클라이언트 소켓
        
    def start(self):
        """
        브로커 서비스 시작
        """
        # 네트워크 트랜스포트 시작
        self.transport.start_server()
        
        # 메시지 핸들러 등록
        self.transport.register_handler('register_service', self._handle_register_service)
        self.transport.register_handler('unregister_service', self._handle_unregister_service)
        self.transport.register_handler('forward_request', self._handle_forward_request)
        self.transport.register_handler('list_services', self._handle_list_services)
        self.transport.register_handler('server_response', self._handle_server_response)
        
        print(f"네트워크 브로커가 시작되었습니다 (ID: {self.broker.broker_id})")
        
    def stop(self):
        """
        브로커 서비스 종료
        """
        self.transport.stop()
        print("네트워크 브로커가 종료되었습니다.")
        
    def _handle_register_service(self, payload, client_sock):
        """
        서비스 등록 처리
        """
        try:
            # 서비스 정보 추출
            service_info_dict = payload.get('service_info', {})
            
            # 디버깅용 출력
            print(f"브로커에 수신된 서비스 등록 정보: {service_info_dict}")
            
            # 서비스 정보가 딕셔너리인 경우 ServiceInfo 객체로 변환
            if isinstance(service_info_dict, dict):
                service_info = ServiceInfo.from_dict(service_info_dict)
            else:
                service_info = service_info_dict
            
            # 등록 처리
            # service_name이 있는지 확인하고 없으면 오류 반환
            if not service_info.service_name:
                return {
                    'success': False,
                    'error': '서비스 이름이 필요합니다.'
                }
            
            # 서비스 등록
            success = self.broker.register_service(service_info)
            
            # 브로커 내부 서비스 목록 디버깅용 출력
            print(f"현재 등록된 서비스 목록: {list(self.broker.services.keys())}")
            
            # 클라이언트 소켓과 서버 ID 연결 저장
            if hasattr(service_info, 'server_id') and service_info.server_id:
                self.server_connections[service_info.server_id] = client_sock
            
            # 응답 생성
            return {
                'success': success,
                'service_id': service_info.service_id if hasattr(service_info, 'service_id') else None
            }
        except Exception as e:
            print(f"서비스 등록 중 오류: {str(e)}")
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
            
    def _handle_unregister_service(self, payload, client_sock):
        """
        서비스 등록 해제 요청 처리
        """
        try:
            # 페이로드 파싱
            server_id = payload.get('server_id')
            
            # 서버 연결 매핑 제거
            if server_id in self.server_connections:
                del self.server_connections[server_id]
            
            # 로컬 브로커에서 서비스 등록 해제
            success = self.broker.unregister_service(server_id)
            
            # 응답 반환
            return {
                'type': 'unregister_service_response',
                'payload': {
                    'success': success
                }
            }
        except Exception as e:
            return {
                'type': 'unregister_service_response',
                'payload': {
                    'success': False,
                    'error': str(e)
                }
            }
            
    def _handle_forward_request(self, payload, client_sock):
        """요청 전달 처리"""
        try:
            # 요청 추출
            request_dict = payload.get('request')
            request = Request.from_dict(request_dict)
            
            print(f"[브로커] 요청 수신: {request.service_name}.{request.method_name}() (요청 ID: {request.message_id}, 클라이언트: {client_sock.getpeername() if hasattr(client_sock, 'getpeername') else 'Unknown'})")
            
            # 서비스 검색 (find_service 메서드 사용)
            service_id = self.broker.find_service(request.service_name)
            if not service_id:
                print(f"[브로커] 서비스를 찾을 수 없음: {request.service_name}")
                return self._send_error_response(
                    f"서비스를 찾을 수 없음: {request.service_name}",
                    request.message_id,
                    client_sock
                )
            
            # 서비스 서버 소켓 검색
            if service_id not in self.server_connections:
                print(f"[브로커] 서버 연결을 찾을 수 없음: {service_id}")
                return self._send_error_response(
                    f"서버 연결을 찾을 수 없음: {service_id}",
                    request.message_id,
                    client_sock
                )
            
            server_sock = self.server_connections[service_id]
            
            # 요청 ID와 클라이언트 소켓 매핑 저장
            self.request_connections[request.message_id] = client_sock
            print(f"[브로커] 요청 매핑 저장: {request.message_id} -> {client_sock.getpeername() if hasattr(client_sock, 'getpeername') else 'Unknown'}")
            
            # 서버에 요청 전송
            print(f"[브로커] 서버에 요청 전달: {request.service_name}.{request.method_name}() (요청 ID: {request.message_id})")
            self.transport.send_message(
                {
                    'type': 'server_request',
                    'payload': {
                        'request': request_dict
                    }
                },
                server_sock
            )
            
            return None
        except Exception as e:
            print(f"[브로커] 요청 전달 처리 중 오류: {str(e)}")
            traceback.print_exc()
            return None
            
    def _send_response(self, response_dict, client_sock):
        """
        클라이언트에게 응답 전송
        """
        response_message = {
            'type': 'forward_request_response',
            'payload': {
                'response': response_dict
            }
        }
        self.transport.send_message(response_message, client_sock)
            
    def _handle_list_services(self, payload, client_sock):
        """
        서비스 목록 요청 처리
        """
        try:
            # 브로커에서 서비스 목록 조회
            services = []
            
            # 브로커에 서비스가 등록되어 있는지 확인
            if hasattr(self.broker, 'services'):
                services = list(self.broker.services.keys())
            
            print(f"브로커 서비스 목록 요청에 응답: {services}")
            
            # 응답 생성
            return {
                'services': services  # 중첩 구조 제거, 간단하게 직접 반환
            }
        except Exception as e:
            print(f"서비스 목록 요청 처리 중 오류: {str(e)}")
            traceback.print_exc()
            return {
                'services': [],
                'error': str(e)
            }
            
    def _handle_server_response(self, payload, client_sock):
        """서버 응답을 클라이언트에게 전달"""
        try:
            # 응답 추출
            response_dict = payload.get('response')
            response = Response.from_dict(response_dict)
            
            print(f"[브로커] 서버 응답 수신: (요청 ID: {response.request_id}, 서버: {client_sock.getpeername() if hasattr(client_sock, 'getpeername') else 'Unknown'})")
            
            # 요청 ID로 원래 클라이언트 소켓 찾기
            request_id = response.request_id
            if request_id in self.request_connections:
                client_sock = self.request_connections[request_id]
                print(f"[브로커] 클라이언트 소켓 찾음: {client_sock.getpeername() if hasattr(client_sock, 'getpeername') else 'Unknown'} (요청 ID: {request_id})")
                
                # 응답 전달
                print(f"[브로커] 클라이언트에 응답 전달: (요청 ID: {request_id})")
                self._send_response(response_dict, client_sock)
                
                # 매핑 제거
                del self.request_connections[request_id]
            else:
                print(f"[브로커] 경고: 요청 ID {request_id}에 해당하는 클라이언트를 찾을 수 없습니다.")
                print(f"[브로커] 현재 요청 매핑: {self.request_connections}")
            
            return None
        except Exception as e:
            print(f"[브로커] 서버 응답 처리 중 오류: {str(e)}")
            traceback.print_exc()
            return None 