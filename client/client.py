# 구현 예정:
# 1. Client 클래스:
#   - ClientProxy를 통해 서비스 요청
#   - 브로커 연결 및 서비스 탐색 

from typing import Any, Dict, List, Optional
from client.client_proxy import ClientProxy

class Client:
    """
    서비스를 요청하는 클라이언트
    """
    
    def __init__(self, broker: Any):
        """
        클라이언트 초기화
        
        Args:
            broker: 브로커 객체
        """
        self.broker = broker
        self.proxies: Dict[str, ClientProxy] = {}
    
    def get_service(self, service_name: str) -> Optional[ClientProxy]:
        """
        서비스 프록시 가져오기
        
        Args:
            service_name: 사용할 서비스 이름
            
        Returns:
            서비스 프록시 (서비스가 없으면 None)
        """
        # 서비스가 존재하는지 확인
        available_services = self.broker.list_services()
        if service_name not in available_services:
            return None
        
        # 프록시가 이미 생성되었는지 확인
        if service_name not in self.proxies:
            self.proxies[service_name] = ClientProxy(self.broker, service_name)
            
        return self.proxies[service_name]
    
    def list_services(self) -> List[str]:
        """
        사용 가능한 서비스 목록 반환
        
        Returns:
            서비스 이름 목록
        """
        return self.broker.list_services() 