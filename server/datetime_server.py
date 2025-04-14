import datetime
from server.network_server import NetworkServer

class DateTimeServer(NetworkServer):
    """
    날짜 및 시간 처리 기능을 제공하는 서버
    """
    
    def __init__(self, broker_host='localhost', broker_port=5000):
        """
        날짜/시간 서버 초기화
        """
        super().__init__(
            broker_host=broker_host,
            broker_port=broker_port,
            service_name="DateTimeService", 
            description="날짜 및 시간 처리 서비스"
        )
    
    def get_current_time(self):
        """
        현재 시간을 ISO 형식으로 반환
        """
        return datetime.datetime.now().isoformat()
    
    def get_current_date(self):
        """
        현재 날짜를 ISO 형식으로 반환
        """
        return datetime.date.today().isoformat()
    
    def format_date(self, date_string, format_string="%Y-%m-%d"):
        """
        날짜 문자열을 지정된 형식으로 포맷팅
        """
        date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d")
        return date_obj.strftime(format_string)
    
    def days_between(self, start_date, end_date):
        """
        두 날짜 사이의 일수 계산
        """
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        delta = end - start
        return delta.days
    
    def is_weekend(self, date_string):
        """
        지정된 날짜가 주말인지 확인
        """
        date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
        return date_obj.weekday() >= 5  # 5=토요일, 6=일요일
    
    def add_days(self, date_string, days):
        """
        날짜에 일수 추가
        """
        date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
        new_date = date_obj + datetime.timedelta(days=days)
        return new_date.isoformat() 