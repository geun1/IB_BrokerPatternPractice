# 구현 예정:
# 1. 브로커에 연결
# 2. "Calculator" 서비스 찾기
# 3. 계산 요청 전송 및 결과 출력 

from client.client import Client

def run_calculator_client(broker):
    """
    계산기 클라이언트 실행
    
    Args:
        broker: 브로커 객체
    """
    # 클라이언트 생성
    client = Client(broker)
    
    # 사용 가능한 서비스 목록 출력
    print("사용 가능한 서비스:", client.list_services())
    
    # 계산기 서비스 가져오기
    calculator = client.get_service("Calculator")
    if not calculator:
        print("계산기 서비스를 찾을 수 없습니다.")
        return
    
    # 계산기 서비스 사용
    try:
        # 덧셈
        result = calculator.add(a=5, b=3)
        print(f"5 + 3 = {result}")
        
        # 뺄셈
        result = calculator.subtract(a=10, b=4)
        print(f"10 - 4 = {result}")
        
        # 곱셈
        result = calculator.multiply(a=6, b=7)
        print(f"6 * 7 = {result}")
        
        # 나눗셈
        result = calculator.divide(a=15, b=3)
        print(f"15 / 3 = {result}")
        
        # 0으로 나누기 시도 (예외 발생)
        try:
            result = calculator.divide(a=8, b=0)
            print(f"8 / 0 = {result}")
        except Exception as e:
            print(f"예상된 오류 발생: {e}")
        
    except Exception as e:
        print(f"오류 발생: {e}") 