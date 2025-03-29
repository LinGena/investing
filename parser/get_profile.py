from bs4 import BeautifulSoup
import json
from logging import Logger as LoggingLogger


class GetProfileData():
    def __init__(self, page_content: str, logger: LoggingLogger = None):
        self.page_content = page_content
        if logger:
            self.logger = logger

    def get(self) -> dict:
        try:
            soup = BeautifulSoup(self.page_content,'html.parser')
            script_data = soup.find('script',{'type':'application/ld+json'})
            if not script_data:
                raise Exception('There is not tag script with type = application/ld+json')
            datas = json.loads(script_data.text.strip())
            return datas
        except Exception as ex: 
            if hasattr(self, 'logger'):
                self.logger.error(ex)
            else:
                print(ex)
        return None  