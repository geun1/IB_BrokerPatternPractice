from broker.network_broker import NetworkBroker
import time
import signal
import sys

def signal_handler(sig, frame):
    print("\n브로커 종료 중...")
    broker.stop()
    sys.exit(0)

if __name__ == "__main__":
    # 브로커 생성 및 시작
    broker = NetworkBroker(host='localhost', port=5000)
    broker.start()
    
    # 시그널 핸들러 등록 (Ctrl+C 처리)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("브로커 서버 실행 중... (종료하려면 Ctrl+C를 누르세요)")
    
    # 메인 스레드 유지
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        broker.stop() 