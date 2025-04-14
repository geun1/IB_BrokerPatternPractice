import socket
import threading
import json
import time
from common.serializer import Serializer
import struct
import traceback

class NetworkTransport:
    """
    네트워크를 통한 메시지 전송 및 수신 처리
    """
    
    def __init__(self, host='localhost', port=5000):
        """
        네트워크 전송 계층 초기화
        
        Args:
            host: 호스트 주소
            port: 포트 번호
        """
        self.host = host
        self.port = port
        self.socket = None
        self.is_server = False
        self.clients = {}  # 서버일 경우 클라이언트 연결 관리
        self.handlers = {}  # 메시지 핸들러
        self.running = False
        self.listener_thread = None
        
    def start_server(self):
        """
        서버 모드로 시작
        """
        self.is_server = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(10)
        
        self.running = True
        self.listener_thread = threading.Thread(target=self._listen_for_clients)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        
        print(f"서버가 {self.host}:{self.port}에서 시작되었습니다.")
        
    def connect_to_server(self):
        """
        클라이언트 모드로 서버에 연결
        """
        if self.is_server:
            raise Exception("서버 모드에서는 서버에 연결할 수 없습니다.")
            
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        
        self.running = True
        self.listener_thread = threading.Thread(target=self._listen_for_messages)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        
        print(f"서버 {self.host}:{self.port}에 연결되었습니다.")
        
    def _listen_for_clients(self):
        """
        서버 모드에서 클라이언트 연결 수신
        """
        while self.running:
            try:
                client_sock, client_addr = self.socket.accept()
                client_id = f"{client_addr[0]}:{client_addr[1]}"
                self.clients[client_id] = client_sock
                
                # 클라이언트별로 메시지 수신 스레드 시작
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_sock, client_id)
                )
                client_thread.daemon = True
                client_thread.start()
                
                print(f"클라이언트 {client_id} 연결됨")
            except Exception as e:
                if self.running:
                    print(f"클라이언트 연결 오류: {e}")
                
    def _handle_client(self, client_sock, client_id):
        """
        클라이언트 요청 처리
        """
        try:
            while self.running:
                # 메시지 길이 먼저 수신 (4바이트)
                length_bytes = client_sock.recv(4)
                if not length_bytes:
                    break
                    
                message_length = int.from_bytes(length_bytes, byteorder='big')
                
                # 메시지 내용 수신
                message_data = b""
                remaining = message_length
                
                while remaining > 0:
                    chunk = client_sock.recv(min(4096, remaining))
                    if not chunk:
                        break
                    message_data += chunk
                    remaining -= len(chunk)
                
                if len(message_data) < message_length:
                    print(f"불완전한 메시지 수신: {len(message_data)}/{message_length}")
                    break
                
                # 메시지 역직렬화 및 처리
                message_str = message_data.decode('utf-8')
                self._handle_client_message(client_sock, message_str)
                
        except Exception as e:
            print(f"클라이언트 {client_id} 처리 오류: {e}")
        finally:
            # 연결 종료 처리
            client_sock.close()
            if client_id in self.clients:
                del self.clients[client_id]
            print(f"클라이언트 {client_id} 연결 종료")
                
    def _listen_for_messages(self):
        """
        클라이언트 모드에서 서버 메시지 수신
        """
        try:
            while self.running:
                # 메시지 길이 먼저 수신 (4바이트)
                length_bytes = self.socket.recv(4)
                if not length_bytes:
                    break
                    
                message_length = int.from_bytes(length_bytes, byteorder='big')
                
                # 메시지 내용 수신
                message_data = b""
                remaining = message_length
                
                while remaining > 0:
                    chunk = self.socket.recv(min(4096, remaining))
                    if not chunk:
                        break
                    message_data += chunk
                    remaining -= len(chunk)
                
                # 메시지 역직렬화 및 처리
                message_str = message_data.decode('utf-8')
                self._handle_client_message(self.socket, message_str)
                
        except Exception as e:
            if self.running:
                print(f"서버 메시지 수신 오류: {e}")
        finally:
            if self.running:
                print("서버와 연결이 끊어졌습니다.")
                self.stop()
    
    def _handle_client_message(self, client_sock, data):
        """
        클라이언트로부터 받은 메시지 처리
        """
        try:
            # 메시지 역직렬화
            message = json.loads(data.encode('utf-8'))
            
            # 메시지 타입과 페이로드 확인
            message_type = message.get('type')
            payload = message.get('payload', {})
            
            # 안전한 getpeername 호출
            try:
                peer_info = client_sock.getpeername() if hasattr(client_sock, 'getpeername') else 'Unknown'
            except Exception:
                peer_info = 'Unknown'
            
            print(f"[전송 계층] 메시지 수신: {message_type} (소켓: {peer_info})")
            
            # 핸들러 호출
            if message_type in self.handlers:
                # 핸들러 호출하여 응답 생성
                handler = self.handlers[message_type]
                response_payload = handler(payload, client_sock)
                
                # 응답이 필요하면 전송
                if response_payload is not None:
                    response_message = {
                        'type': f"{message_type}_response",
                        'payload': response_payload
                    }
                    
                    print(f"[전송 계층] 응답 전송: {message_type}_response (소켓: {peer_info})")
                    self.send_message(response_message, client_sock)
            else:
                print(f"[전송 계층] 처리할 수 없는 메시지 타입: {message_type}")
        except json.JSONDecodeError:
            print("[전송 계층] JSON 디코딩 오류")
        except Exception as e:
            print(f"[전송 계층] 메시지 처리 중 오류: {str(e)}")
            # 예외 스택 트레이스 기록(옵션)
            traceback.print_exc()
    
    def send_message(self, message, client_sock=None):
        """
        메시지 전송
        """
        try:
            # 메시지 직렬화
            serialized_message = json.dumps(message).encode('utf-8')
            
            # 메시지 길이 계산 (4바이트)
            message_length = len(serialized_message)
            message_length_bytes = struct.pack('!I', message_length)
            
            # 안전한 소켓 상태 확인
            if client_sock is None:
                # 서버 소켓 확인
                if not self.socket or not hasattr(self.socket, 'sendall'):
                    print("[전송 계층] 오류: 서버 소켓이 유효하지 않음")
                    return
                    
                try:
                    peer_info = "서버"
                    print(f"[전송 계층] 서버에 메시지 전송: {message['type']} (크기: {message_length}바이트)")
                    self.socket.sendall(message_length_bytes + serialized_message)
                except Exception as e:
                    print(f"[전송 계층] 서버 메시지 전송 오류: {str(e)}")
            else:
                # 클라이언트 소켓 확인
                if not hasattr(client_sock, 'sendall'):
                    print("[전송 계층] 오류: 클라이언트 소켓이 유효하지 않음")
                    return
                    
                try:
                    # 안전한 getpeername 호출
                    try:
                        peer_info = client_sock.getpeername() if hasattr(client_sock, 'getpeername') else 'Unknown'
                    except Exception:
                        peer_info = 'Unknown'
                        
                    print(f"[전송 계층] 클라이언트에 메시지 전송: {message['type']} (소켓: {peer_info}, 크기: {message_length}바이트)")
                    client_sock.sendall(message_length_bytes + serialized_message)
                except Exception as e:
                    print(f"[전송 계층] 클라이언트 메시지 전송 오류: {str(e)}")
        except Exception as e:
            print(f"[전송 계층] 메시지 전송 중 오류: {str(e)}")
    
    def register_handler(self, message_type, handler):
        """
        메시지 타입별 핸들러 등록
        
        Args:
            message_type: 메시지 타입
            handler: 처리 함수(payload, client_sock를 인자로 받음)
        """
        self.handlers[message_type] = handler
    
    def stop(self):
        """
        네트워크 전송 계층 종료
        """
        self.running = False
        
        if self.is_server:
            # 서버 모드: 모든 클라이언트 연결 종료
            for client_sock in list(self.clients.values()):
                try:
                    client_sock.close()
                except:
                    pass
            self.clients.clear()
        
        # 소켓 종료
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None 