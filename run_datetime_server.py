#!/usr/bin/env python3

import signal
import sys
from server.datetime_server import DateTimeServer

# 날짜/시간 서버 생성
server = DateTimeServer(broker_host='localhost', broker_port=5000)

# 종료 핸들러
def signal_handler(sig, frame):
    print("\n날짜/시간 서버 종료 중...")
    server.stop()
    print("날짜/시간 서버가 종료되었습니다.")
    sys.exit(0)

# 시그널 핸들러 등록
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# 서버 시작
server.start()
print("날짜/시간 서버 실행 중... (종료하려면 Ctrl+C를 누르세요)")

# 메인 스레드 유지
try:
    signal.pause()
except AttributeError:
    # Windows에서는 signal.pause()가 지원되지 않음
    import time
    while True:
        time.sleep(1) 