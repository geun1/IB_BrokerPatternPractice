# 구현 예정:
# 1. ClientProxy 클래스:
#   - 브로커에 요청을 보내는 인터페이스 제공
#   - 요청 직렬화 및 응답 역직렬화
#   - 로컬 메서드 호출처럼 보이게 하는 인터페이스
# 2. 프록시 동적 생성 메커니즘 

from typing import Any, Dict, List
from common.message import Request, Response
from common.serializer import Serializer

class ClientProxy:
    """
    클라이언트와 브로커 사이에서 요청을 중계하는 프록시
    """
    
    def __init__(self, broker: Any, service_name: str):
        """
        클라이언트 프록시 초기화
        
        Args:
            broker: 브로커 객체
            service_name: 사용할 서비스 이름
        """
        self.broker = broker
        self.service_name = service_name
        self.class_registry = {
            'Request': Request,
            'Response': Response
        }
    
    def __getattr__(self, method_name: str) -> Any:
        """
        존재하지 않는 속성에 접근할 때 호출됨
        서비스 메서드 호출을 위한 래퍼 함수 생성
        
        Args:
            method_name: 호출할 메서드 이름
            
        Returns:
            메서드 호출 래퍼 함수
        """
        def method_wrapper(**kwargs):
            return self.call_method(method_name, **kwargs)
        return method_wrapper
    
    def call_method(self, method_name: str, **kwargs) -> Any:
        """
        원격 메서드 호출
        
        Args:
            method_name: 호출할 메서드 이름
            **kwargs: 메서드 매개변수
            
        Returns:
            메서드 호출 결과
        """
        # 요청 생성
        request = Request(
            service_name=self.service_name,
            method_name=method_name,
            parameters=kwargs
        )
        
        # 브로커에 요청 전달
        response = self.broker.forward_request(request)
        
        # 응답 처리
        if not response.success:
            # 오류 발생 시 예외 발생
            raise Exception(f"서비스 호출 오류: {response.error}")
        
        # 성공 시 결과 반환
        return response.result 