# 브로커 패턴 구현 프로젝트

## 프로젝트 개요

브로커 패턴은 분산 시스템에서 서비스 제공자(서버)와 서비스 소비자(클라이언트) 간의 통신을 중재하는 아키텍처 패턴입니다. 이 패턴은 시스템 컴포넌트 간의 결합도를 낮추고, 서비스의 동적 등록 및 검색을 가능하게 합니다.

## 주요 특징

-   **느슨한 결합(Loose Coupling)**: 클라이언트와 서버가 서로의 존재를 직접 알 필요가 없으며, 브로커를 통해서만 통신합니다. 이는 시스템 컴포넌트의 독립적인 개발, 배포, 확장을 가능하게 합니다.
-   **확장성(Scalability)**: 새로운 서비스를 쉽게 추가하고 제거할 수 있습니다. 브로커는 동적으로 서비스를 등록하고 클라이언트 요청을 적절히 라우팅합니다.
-   **유연성(Flexibility)**: 서비스 구현이 변경되더라도 클라이언트 코드를 수정할 필요가 없습니다. 인터페이스가 동일하게 유지되는 한, 서버 측 구현은 자유롭게 변경될 수 있습니다.
-   **동적 서비스 발견(Dynamic Service Discovery)**: 런타임에 서비스를 등록하고 검색할 수 있어, 시스템이 동적으로 변화하는 환경에 적응할 수 있습니다.
-   **위치 투명성(Location Transparency)**: 클라이언트는 서비스의 물리적 위치나 네트워크 주소를 알 필요 없이 논리적 이름만으로 서비스를 호출할 수 있습니다.

## 활용 사례

브로커 패턴은 다음과 같은 시스템에 특히 적합합니다:

1. **마이크로서비스 아키텍처**: 여러 독립적인 서비스로 구성된 시스템에서 서비스 간 통신 관리
2. **IoT 시스템**: 다양한 장치와 서비스 간의 통신 중재
3. **분산 시스템**: 여러 서버에 분산된 서비스의 중앙 관리
4. **클라우드 기반 애플리케이션**: 서비스 인스턴스의 동적 확장 및 축소 지원
5. **이벤트 기반 시스템**: 서비스 간 이벤트 전달 및 관리

## 구현 목표

이 프로젝트의 주요 목표는 다음과 같습니다:

-   브로커 패턴의 핵심 구성 요소 구현
-   네트워크 통신을 통한 원격 서비스 호출 지원
-   동적 서비스 등록 및 검색 기능 제공
-   요청-응답 패턴의 통신 모델 구현
-   다중 클라이언트 및 서버 지원
-   확장 가능한 아키텍처 설계

## 기술 스택

-   **프로그래밍 언어**: Python 3.6+
-   **통신 프로토콜**: TCP/IP 소켓
-   **메시지 형식**: JSON
-   **동시성 처리**: 멀티스레딩
-   **테스트 프레임워크**: unittest

## 시작하기

### 설치 방법

1. 저장소 클론:

    ```bash
    git clone https://github.com/yourusername/broker-pattern.git
    cd broker-pattern
    ```

2. 의존성 설치:
    ```bash
    pip install -r requirements.txt
    ```

### 실행 방법

-   브로커 시작:

    ```bash
    python run_broker.py
    ```

-   샘플 서버 시작:

    ```bash
    python sample_server.py
    ```

-   클라이언트 실행:
    ```bash
    python sample_client.py
    ```

### 테스트 실행

-   모든 테스트 실행:

    ```bash
    python run_broker_tests.py
    ```

-   특정 테스트 실행:
    ```bash
    python -m unittest test.test_service_registration
    ```

## 프로젝트 구조

broker-pattern/
├── broker/
│ ├── broker.py
│ └── network_broker.py
├── client/
│ └── network_client.py
├── common/
│ └── message.py
├── server/
│ ├── server.py
│ └── network_server.py
├── test/
│ ├── run_broker_tests.py
│ ├── test_broker_integration.py
│ └── test_broker_pattern.py
└── README.md

## 주요 컴포넌트 설명

### 브로커 (Broker)

브로커는 이 패턴의 핵심 컴포넌트로서 다음과 같은 역할을 담당합니다:

-   **서비스 등록 관리**: 서버가 제공하는 서비스를 등록, 업데이트, 제거합니다.
-   **요청 라우팅**: 클라이언트의 요청을 적절한 서비스 제공자(서버)에게 전달합니다.
-   **서비스 검색**: 클라이언트가 필요로 하는 서비스를 찾아줍니다.
-   **로드 밸런싱**: 여러 서버가 동일한 서비스를 제공할 경우, 요청을 분산시킵니다.

```python
# broker/broker.py의 핵심 기능
class Broker:
    def __init__(self):
        self.services = {}  # 서비스 레지스트리

    def register_service(self, service_name, service_handler):
        self.services[service_name] = service_handler

    def unregister_service(self, service_name):
        if service_name in self.services:
            del self.services[service_name]

    def get_service(self, service_name):
        return self.services.get(service_name)
```

### 서버 (Server)

서버는 클라이언트에게 제공할 서비스를 구현하고 브로커에 등록합니다:

-   **서비스 구현**: 실제 비즈니스 로직 및 기능을 구현합니다.
-   **서비스 등록**: 시작 시 자신이 제공하는 서비스를 브로커에 등록합니다.
-   **요청 처리**: 브로커를 통해 전달된 클라이언트 요청을 처리합니다.
-   **결과 반환**: 요청 처리 결과를 브로커를 통해 클라이언트에게 반환합니다.

```python
# server/server.py의 핵심 기능
class Server:
    def __init__(self, broker):
        self.broker = broker
        self.services = {}

    def add_service(self, service_name, service_impl):
        self.services[service_name] = service_impl
        self.broker.register_service(service_name, self)

    def handle_request(self, service_name, request):
        service = self.services.get(service_name)
        if service:
            return service.process(request)
        return {"error": "서비스를 찾을 수 없습니다"}
```

### 클라이언트 (Client)

클라이언트는 최종 사용자를 대표하며 서비스를 사용합니다:

-   **서비스 요청**: 브로커를 통해 필요한 서비스를 요청합니다.
-   **서비스 검색**: 사용 가능한 서비스를 브로커에게 질의합니다.
-   **결과 처리**: 서비스 요청의 결과를 수신하고 처리합니다.

```python
# client/network_client.py의 핵심 기능
class Client:
    def __init__(self, broker):
        self.broker = broker

    def call_service(self, service_name, request):
        service = self.broker.get_service(service_name)
        if service:
            return service.handle_request(service_name, request)
        return {"error": "서비스를 찾을 수 없습니다"}

    def discover_services(self):
        return self.broker.get_available_services()
```

### 메시지 (Message)

컴포넌트 간 통신에 사용되는 메시지 형식을 정의합니다:

-   **요청 메시지**: 클라이언트에서 서버로 전송되는 메시지
-   **응답 메시지**: 서버에서 클라이언트로 반환되는 메시지
-   **등록 메시지**: 서버가 브로커에 서비스를 등록할 때 사용하는 메시지

```python
# common/message.py의 핵심 기능
class Message:
    def __init__(self, message_type, service_name, payload=None):
        self.message_type = message_type  # 'REQUEST', 'RESPONSE', 'REGISTER' 등
        self.service_name = service_name
        self.payload = payload or {}

    def to_json(self):
        return json.dumps({
            "type": self.message_type,
            "service": self.service_name,
            "payload": self.payload
        })

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(data["type"], data["service"], data["payload"])
```

## 컴포넌트 간 상호작용

브로커 패턴에서 컴포넌트들은 다음과 같이 상호작용합니다:

1. **서비스 등록 과정**:

    - 서버는 시작 시 자신이 제공하는 서비스를 브로커에 등록합니다.
    - 브로커는 서비스 레지스트리에 서비스 정보를 저장합니다.

2. **서비스 요청 및 응답 과정**:

    - 클라이언트는 브로커에게 특정 서비스를 요청합니다.
    - 브로커는 서비스 레지스트리에서 해당 서비스를 제공하는 서버를 찾습니다.
    - 브로커는 클라이언트의 요청을 적절한 서버로 전달합니다.
    - 서버는 요청을 처리하고 결과를 브로커에게 반환합니다.
    - 브로커는 서버의 응답을 클라이언트에게 전달합니다.

3. **서비스 해제 과정**:
    - 서버가 종료되거나 서비스를 더 이상 제공하지 않을 때, 브로커에게 서비스 해제를 알립니다.
    - 브로커는 서비스 레지스트리에서 해당 서비스를 제거합니다.

## 다음 단계

프로젝트의 다음 단계와 로드맵에 대해 알아보려면 아키텍처 문서를 참조하세요.
