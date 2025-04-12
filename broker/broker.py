# 구현 예정:
# 1. Broker 클래스: 서비스 요청 중계자
#   - 서비스 저장소(repository) 유지
#   - 서버 등록/해제 기능
#   - 클라이언트 요청 처리 및 적절한 서버로 전달
#   - 서버 응답을 클라이언트로 반환
# 2. ServiceRepository 클래스: 서비스 정보 관리 

import uuid
from typing import Dict, Any, List, Optional, Callable
from common.message import Request, Response, ServiceInfo
from common.serializer import Serializer

class ServiceRepository:
    """
    서비스 정보를 저장하고 관리하는 레포지토리
    """
    
    def __init__(self):
        """서비스 레포지토리 초기화"""
        # 서비스 이름을 키로 하고, ServiceInfo 객체의 리스트를 값으로 하는 딕셔너리
        self.services: Dict[str, List[ServiceInfo]] = {}
    
    def register_service(self, service_info: ServiceInfo) -> bool:
        """
        서비스 등록
        
        Args:
            service_info: 등록할 서비스 정보
            
        Returns:
            등록 성공 여부
        """
        service_name = service_info.service_name
        
        if service_name not in self.services:
            self.services[service_name] = []
            
        # 이미 등록된 서버인지 확인
        for existing_service in self.services[service_name]:
            if existing_service.server_id == service_info.server_id:
                # 이미 등록된 서버라면 정보 업데이트
                existing_service.__dict__.update(service_info.__dict__)
                return True
                
        # 신규 서비스 등록
        self.services[service_name].append(service_info)
        return True
    
    def unregister_service(self, server_id: str, service_name: Optional[str] = None) -> bool:
        """
        서비스 등록 해제
        
        Args:
            server_id: 등록 해제할 서버 ID
            service_name: 특정 서비스 이름 (None이면 모든 서비스)
            
        Returns:
            등록 해제 성공 여부
        """
        if service_name:
            # 특정 서비스만 등록 해제
            if service_name in self.services:
                self.services[service_name] = [
                    service for service in self.services[service_name]
                    if service.server_id != server_id
                ]
                # 서비스 목록이 비었다면 키 삭제
                if not self.services[service_name]:
                    del self.services[service_name]
                return True
        else:
            # 모든 서비스에서 해당 서버 제거
            for svc_name in list(self.services.keys()):
                self.services[svc_name] = [
                    service for service in self.services[svc_name]
                    if service.server_id != server_id
                ]
                # 서비스 목록이 비었다면 키 삭제
                if not self.services[svc_name]:
                    del self.services[svc_name]
            return True
        
        return False
    
    def find_service(self, service_name: str) -> Optional[ServiceInfo]:
        """
        서비스 이름으로 서비스 정보 찾기
        
        Args:
            service_name: 찾을 서비스 이름
            
        Returns:
            찾은 서비스 정보 (없으면 None)
        """
        if service_name in self.services and self.services[service_name]:
            # 간단한 로드 밸런싱: 첫 번째 서비스 반환
            # 실제 구현에서는 더 복잡한 로드 밸런싱 전략을 사용할 수 있음
            return self.services[service_name][0]
        return None
    
    def list_services(self) -> List[str]:
        """
        등록된 모든 서비스 이름 목록 반환
        
        Returns:
            서비스 이름 목록
        """
        return list(self.services.keys())
    
    def get_service_info(self, service_name: str) -> List[ServiceInfo]:
        """
        특정 서비스의 모든 인스턴스 정보 반환
        
        Args:
            service_name: 서비스 이름
            
        Returns:
            서비스 정보 목록
        """
        return self.services.get(service_name, [])


class Broker:
    """
    브로커 패턴의 중앙 중개자 역할을 하는 클래스
    """
    
    def __init__(self):
        """브로커 초기화"""
        self.repository = ServiceRepository()
        self.server_handlers: Dict[str, Callable] = {}
        self.broker_id = str(uuid.uuid4())
        
    def register_service(self, service_info: ServiceInfo) -> bool:
        """
        서비스 등록
        
        Args:
            service_info: 등록할 서비스 정보
            
        Returns:
            등록 성공 여부
        """
        return self.repository.register_service(service_info)
    
    def unregister_service(self, server_id: str, service_name: Optional[str] = None) -> bool:
        """
        서비스 등록 해제
        
        Args:
            server_id: 등록 해제할 서버 ID
            service_name: 특정 서비스 이름 (None이면 모든 서비스)
            
        Returns:
            등록 해제 성공 여부
        """
        return self.repository.unregister_service(server_id, service_name)
    
    def register_server_handler(self, server_id: str, handler: Callable) -> None:
        """
        서버 핸들러 등록 (메시지를 전달할 콜백 함수)
        
        Args:
            server_id: 서버 ID
            handler: 메시지 처리 핸들러 함수
        """
        self.server_handlers[server_id] = handler
    
    def unregister_server_handler(self, server_id: str) -> None:
        """
        서버 핸들러 등록 해제
        
        Args:
            server_id: 서버 ID
        """
        if server_id in self.server_handlers:
            del self.server_handlers[server_id]
    
    def forward_request(self, request: Request) -> Response:
        """
        클라이언트 요청을 적절한 서버로 전달
        
        Args:
            request: 처리할 요청
            
        Returns:
            서버의 응답
        """
        service_name = request.service_name
        service_info = self.repository.find_service(service_name)
        
        if not service_info:
            # 서비스를 찾을 수 없음
            return Response(
                error=f"서비스를 찾을 수 없음: {service_name}",
                request_id=request.message_id
            )
        
        server_id = service_info.server_id
        if server_id not in self.server_handlers:
            # 서버 핸들러를 찾을 수 없음
            return Response(
                error=f"서버 핸들러를 찾을 수 없음: {server_id}",
                request_id=request.message_id
            )
        
        # 서버 핸들러를 통해 요청 전달
        handler = self.server_handlers[server_id]
        # 직렬화된 요청을 전달하고 응답 받기
        serialized_request = Serializer.serialize(request)
        serialized_response = handler(serialized_request)
        
        # 응답 역직렬화 후 반환
        response = Serializer.deserialize(serialized_response)
        return response
    
    def list_services(self) -> List[str]:
        """
        등록된 모든 서비스 이름 목록 반환
        
        Returns:
            서비스 이름 목록
        """
        return self.repository.list_services()
    
    def get_service_info(self, service_name: str) -> List[ServiceInfo]:
        """
        특정 서비스의 모든 인스턴스 정보 반환
        
        Args:
            service_name: 서비스 이름
            
        Returns:
            서비스 정보 목록
        """
        return self.repository.get_service_info(service_name) 