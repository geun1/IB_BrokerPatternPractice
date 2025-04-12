# 구현 예정:
# 1. 객체를 직렬화하는 함수 (dict, JSON 등으로 변환)
# 2. 직렬화된 데이터를 역직렬화하는 함수
# 3. 다양한 데이터 타입 지원 (기본 타입, 객체 등) 

import json
import inspect
from typing import Any, Dict, Type

class Serializer:
    """
    객체를 직렬화하고 역직렬화하는 유틸리티 클래스
    """
    
    @staticmethod
    def serialize(obj: Any) -> str:
        """
        객체를 JSON 문자열로 직렬화합니다.
        
        Args:
            obj: 직렬화할 객체
            
        Returns:
            직렬화된 JSON 문자열
        """
        if hasattr(obj, 'to_dict'):
            # 객체가 to_dict 메서드를 가지고 있으면 해당 메서드 사용
            serialized_dict = obj.to_dict()
            # 클래스 정보 추가
            serialized_dict['__class__'] = obj.__class__.__name__
            serialized_dict['__module__'] = obj.__class__.__module__
            return json.dumps(serialized_dict)
        else:
            # 기본 직렬화 사용
            return json.dumps(obj)
    
    @staticmethod
    def deserialize(json_str: str, class_registry: Dict[str, Type] = None) -> Any:
        """
        JSON 문자열을 객체로 역직렬화합니다.
        
        Args:
            json_str: 역직렬화할 JSON 문자열
            class_registry: 클래스 이름과 클래스 타입의 매핑 딕셔너리
            
        Returns:
            역직렬화된 객체
        """
        obj_dict = json.loads(json_str)
        
        # 기본 타입이면 그대로 반환
        if not isinstance(obj_dict, dict):
            return obj_dict
            
        # 클래스 정보가 있는지 확인
        if '__class__' in obj_dict and '__module__' in obj_dict:
            class_name = obj_dict.pop('__class__')
            module_name = obj_dict.pop('__module__')
            
            # class_registry에서 클래스 찾기
            if class_registry and class_name in class_registry:
                class_type = class_registry[class_name]
            else:
                # 동적으로 클래스 가져오기
                try:
                    module = __import__(module_name, fromlist=[class_name])
                    class_type = getattr(module, class_name)
                except (ImportError, AttributeError):
                    # 클래스를 찾을 수 없으면 딕셔너리 반환
                    return obj_dict
            
            # 클래스에 from_dict 메서드가 있으면 사용
            if hasattr(class_type, 'from_dict'):
                return class_type.from_dict(obj_dict)
            
            # 없으면 생성자에 인자로 전달
            try:
                return class_type(**obj_dict)
            except TypeError:
                # 생성자 호출 실패 시 딕셔너리 반환
                return obj_dict
        
        # 클래스 정보가 없으면 그대로 반환
        return obj_dict 