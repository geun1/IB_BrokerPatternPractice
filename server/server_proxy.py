# 구현 예정:
# 1. ServerProxy 클래스:
#   - 브로커로부터 요청 수신
#   - 요청 역직렬화 및 응답 직렬화
#   - 실제 서버 메서드 호출 

from typing import Dict, Any, Callable, Type
from common.message import Request, Response
from common.serializer import Serializer

class ServerProxy:
    """
    서버와 브로커 사이에서 메시지를 중계하는 프록시
    """
    
    def __init__(self, server: Any):
        """
        서버 프록시 초기화
        
        Args:
            server: 실제 서비스를 제공하는 서버 객체
        """
        self.server = server
        self.class_registry: Dict[str, Type] = {
            'Request': Request,
            'Response': Response
        }
    
    def handle_request(self, serialized_request: str) -> str:
        """
        브로커로부터 받은 요청을 처리
        
        Args:
            serialized_request: 직렬화된 요청 문자열
            
        Returns:
            직렬화된 응답 문자열
        """
        try:
            # 요청 역직렬화
            request = Serializer.deserialize(serialized_request, self.class_registry)
            
            if not isinstance(request, Request):
                # 유효하지 않은 요청
                response = Response(
                    error="유효하지 않은 요청 형식",
                    request_id=getattr(request, 'message_id', None)
                )
                return Serializer.serialize(response)
            
            # 서버에서 메서드 찾기
            method_name = request.method_name
            if not hasattr(self.server, method_name):
                # 메서드를 찾을 수 없음
                response = Response(
                    error=f"메서드를 찾을 수 없음: {method_name}",
                    request_id=request.message_id
                )
                return Serializer.serialize(response)
            
            # 메서드 실행
            method = getattr(self.server, method_name)
            result = method(**request.parameters)
            
            # 응답 생성 및 직렬화
            response = Response(
                result=result,
                request_id=request.message_id
            )
            return Serializer.serialize(response)
            
        except Exception as e:
            # 요청 처리 중 오류 발생
            error_response = Response(
                error=f"요청 처리 중 오류: {str(e)}",
                request_id=getattr(request, 'message_id', None) if 'request' in locals() else None
            )
            return Serializer.serialize(error_response) 