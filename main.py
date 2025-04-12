# 구현 예정:
# 1. 브로커 인스턴스 생성 및 시작
# 2. 서버 인스턴스 생성 및 등록
# 3. 클라이언트 생성 및 요청 실행
# 4. 전체 흐름 테스트 

from broker.broker import Broker
from examples.calculator_server import CalculatorServer
from examples.calculator_client import run_calculator_client

def main():
    """
    브로커 패턴 테스트를 위한 메인 함수
    """
    # 브로커 생성
    broker = Broker()
    print(f"브로커 생성 (ID: {broker.broker_id})")
    
    # 서버 생성 및 시작
    calc_server = CalculatorServer(broker)
    calc_server.start()
    print(f"계산기 서버 시작 (ID: {calc_server.server_id})")
    
    # 클라이언트 실행
    print("\n=== 클라이언트 실행 ===")
    run_calculator_client(broker)
    
    # 서버 종료
    calc_server.stop()
    print("\n계산기 서버 종료")

if __name__ == "__main__":
    main() 