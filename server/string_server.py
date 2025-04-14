from server.network_server import NetworkServer

class StringServer(NetworkServer):
    """
    문자열 처리 기능을 제공하는 서버
    """
    
    def __init__(self, broker_host='localhost', broker_port=5000):
        """
        문자열 서버 초기화
        """
        super().__init__(
            broker_host=broker_host,
            broker_port=broker_port,
            service_name="StringService",
            description="문자열 처리 서비스"
        )
    
    def reverse(self, text):
        """
        문자열을 뒤집어 반환
        """
        return text[::-1]
    
    def upper(self, text):
        """
        문자열을 대문자로 변환
        """
        return text.upper()
    
    def lower(self, text):
        """
        문자열을 소문자로 변환
        """
        return text.lower()
    
    def concat(self, texts):
        """
        문자열 목록을 연결
        """
        return "".join(texts)
    
    def split(self, text, delimiter=" "):
        """
        문자열을 구분자로 분리
        """
        return text.split(delimiter)
    
    def count(self, text, substring):
        """
        부분 문자열 개수 계산
        """
        return text.count(substring) 