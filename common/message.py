# 구현 예정:
# 1. Message 클래스: 요청과 응답을 위한 기본 클래스
# 2. Request 클래스: 서비스 이름, 메서드, 매개변수 등 포함
# 3. Response 클래스: 결과, 오류 정보 등 포함
# 4. ServiceInfo 클래스: 서버 서비스 정보 저장 

from typing import Any, Dict, List, Optional
import uuid

class Message:
    """
    요청과 응답을 위한 기본 메시지 클래스
    """
    
    def __init__(self, message_id: str = None):
        """
        메시지 초기화
        
        Args:
            message_id: 메시지 고유 ID (지정하지 않으면 자동 생성)
        """
        self.message_id = message_id or str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        메시지를 딕셔너리로 변환
        
        Returns:
            메시지 속성이 담긴 딕셔너리
        """
        return {
            'message_id': self.message_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        딕셔너리에서 메시지 객체 생성
        
        Args:
            data: 메시지 데이터가 담긴 딕셔너리
            
        Returns:
            생성된 메시지 객체
        """
        return cls(message_id=data.get('message_id'))


class Request(Message):
    """
    서비스 요청을 위한 메시지 클래스
    """
    
    def __init__(self, service_name: str, method_name: str, 
                 parameters: Dict[str, Any] = None, message_id: str = None):
        """
        요청 메시지 초기화
        
        Args:
            service_name: 요청할 서비스 이름
            method_name: 호출할 메서드 이름
            parameters: 메서드 호출에 필요한 매개변수
            message_id: 메시지 고유 ID
        """
        super().__init__(message_id)
        self.service_name = service_name
        self.method_name = method_name
        self.parameters = parameters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        요청을 딕셔너리로 변환
        
        Returns:
            요청 속성이 담긴 딕셔너리
        """
        data = super().to_dict()
        data.update({
            'service_name': self.service_name,
            'method_name': self.method_name,
            'parameters': self.parameters
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Request':
        """
        딕셔너리에서 요청 객체 생성
        
        Args:
            data: 요청 데이터가 담긴 딕셔너리
            
        Returns:
            생성된 요청 객체
        """
        return cls(
            service_name=data.get('service_name', ''),
            method_name=data.get('method_name', ''),
            parameters=data.get('parameters', {}),
            message_id=data.get('message_id')
        )


class Response(Message):
    """
    서비스 응답을 위한 메시지 클래스
    """
    
    def __init__(self, result: Any = None, error: str = None, 
                 request_id: str = None, message_id: str = None):
        """
        응답 메시지 초기화
        
        Args:
            result: 요청 처리 결과
            error: 오류 메시지 (있는 경우)
            request_id: 원본 요청의 ID
            message_id: 메시지 고유 ID
        """
        super().__init__(message_id)
        self.result = result
        self.error = error
        self.request_id = request_id
        self.success = error is None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        응답을 딕셔너리로 변환
        
        Returns:
            응답 속성이 담긴 딕셔너리
        """
        data = super().to_dict()
        data.update({
            'result': self.result,
            'error': self.error,
            'request_id': self.request_id,
            'success': self.success
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Response':
        """
        딕셔너리에서 응답 객체 생성
        
        Args:
            data: 응답 데이터가 담긴 딕셔너리
            
        Returns:
            생성된 응답 객체
        """
        return cls(
            result=data.get('result'),
            error=data.get('error'),
            request_id=data.get('request_id'),
            message_id=data.get('message_id')
        )


class ServiceInfo:
    """
    서비스 정보를 저장하는 클래스
    """
    
    def __init__(self, service_name: str, methods: List[str], 
                 server_id: str, description: str = ""):
        """
        서비스 정보 초기화
        
        Args:
            service_name: 서비스 이름
            methods: 제공하는 메서드 목록
            server_id: 서버 식별자
            description: 서비스 설명
        """
        self.service_name = service_name
        self.methods = methods
        self.server_id = server_id
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """
        서비스 정보를 딕셔너리로 변환
        
        Returns:
            서비스 정보가 담긴 딕셔너리
        """
        return {
            'service_name': self.service_name,
            'methods': self.methods,
            'server_id': self.server_id,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceInfo':
        """
        딕셔너리에서 서비스 정보 객체 생성
        
        Args:
            data: 서비스 정보가 담긴 딕셔너리
            
        Returns:
            생성된 서비스 정보 객체
        """
        return cls(
            service_name=data.get('service_name', ''),
            methods=data.get('methods', []),
            server_id=data.get('server_id', ''),
            description=data.get('description', '')
        ) 