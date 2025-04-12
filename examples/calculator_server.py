# 구현 예정:
# 1. CalculatorServer 클래스:
#   - 덧셈, 뺄셈, 곱셈, 나눗셈 등 기본 연산 제공
#   - Server 클래스 상속
#   - 브로커에 "Calculator" 서비스로 등록 

from server.server import Server

class CalculatorServer(Server):
    """
    기본 계산 기능을 제공하는 서비스
    """
    
    def __init__(self, broker):
        """
        계산기 서버 초기화
        
        Args:
            broker: 브로커 객체
        """
        super().__init__(
            broker=broker,
            service_name="Calculator",
            description="기본 사칙연산을 제공하는 계산기 서비스"
        )
    
    def add(self, a: float, b: float) -> float:
        """
        두 수의 합 계산
        
        Args:
            a: 첫 번째 숫자
            b: 두 번째 숫자
            
        Returns:
            a + b 결과
        """
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """
        두 수의 차 계산
        
        Args:
            a: 첫 번째 숫자
            b: 두 번째 숫자
            
        Returns:
            a - b 결과
        """
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """
        두 수의 곱 계산
        
        Args:
            a: 첫 번째 숫자
            b: 두 번째 숫자
            
        Returns:
            a * b 결과
        """
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """
        두 수의 나눗셈 계산
        
        Args:
            a: 첫 번째 숫자
            b: 두 번째 숫자
            
        Returns:
            a / b 결과
            
        Raises:
            ZeroDivisionError: b가 0인 경우
        """
        if b == 0:
            raise ZeroDivisionError("0으로 나눌 수 없습니다")
        return a / b 