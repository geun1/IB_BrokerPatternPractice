"""
서비스 제공자 인터페이스 정의

주요 기능:
1. 서비스 등록: 브로커에 서비스 정보 등록
2. 메서드 구현: 서비스에서 제공할 메서드 구현
3. 요청 처리: 클라이언트로부터 전달된 요청 처리
4. 응답 반환: 요청 처리 결과 반환

추상 클래스로 서비스 서버의 기본 동작 정의
"""

# 구현 예정:
# 1. Server 클래스:
#   - 서비스 구현 및 제공
#   - 브로커에 서비스 등록/해제
#   - 서비스 요청 처리
# 2. ServiceImplementation: 서비스 인터페이스 

import uuid
import inspect
from typing import Dict, List, Any, Callable
from common.message import ServiceInfo
from server.server_proxy import ServerProxy

class Server:
    """
    서비스를 제공하는 서버 기본 클래스
    """
    
    def __init__(self, broker: Any, service_name: str, description: str = ""):
        """
        서버 초기화
        
        Args:
            broker: 브로커 객체
            service_name: 서비스 이름
            description: 서비스 설명
        """
        self.broker = broker
        self.service_name = service_name
        self.description = description
        self.server_id = str(uuid.uuid4())
        self.proxy = ServerProxy(self)
        
        # 브로커에 핸들러 등록
        self.broker.register_server_handler(
            self.server_id, 
            self.proxy.handle_request
        )
    
    def start(self) -> bool:
        """
        서버 시작 및 서비스 등록
        
        Returns:
            성공 여부
        """
        # 제공할 메서드 목록 추출
        methods = self._get_service_methods()
        
        # 서비스 정보 생성
        service_info = ServiceInfo(
            service_name=self.service_name,
            methods=methods,
            server_id=self.server_id,
            description=self.description
        )
        
        # 브로커에 서비스 등록
        return self.broker.register_service(service_info)
    
    def stop(self) -> bool:
        """
        서버 종료 및 서비스 등록 해제
        
        Returns:
            성공 여부
        """
        # 브로커에서 서버 핸들러 등록 해제
        self.broker.unregister_server_handler(self.server_id)
        
        # 브로커에서 서비스 등록 해제
        return self.broker.unregister_service(self.server_id)
    
    def _get_service_methods(self) -> List[str]:
        """
        이 서버가 제공하는 서비스 메서드 목록 반환
        
        Returns:
            메서드 이름 목록
        """
        # 상속받은 메서드 제외 및 내부 메서드(_로 시작) 제외
        methods = []
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if not name.startswith('_') and name not in ['start', 'stop']:
                methods.append(name)
        return methods 