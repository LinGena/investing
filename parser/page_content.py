from driver.dynamic import UndetectedDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
from datetime import datetime
from parser.get_key_statistic import GetKeyStatistic
from parser.get_profile import GetProfileData
from parser.get_historical_data import GetHistoricalData
from db.queries import Queries
from selenium.webdriver.common.keys import Keys


class PageContent(UndetectedDriver):
    def __init__(self, first_create: bool = False):
        super().__init__(first_create)
        self.wait = lambda time_w, criteria: WebDriverWait(self.driver, time_w).until(
            EC.presence_of_element_located(criteria))
        self.chain = ActionChains(self.driver)
        self.queries = Queries()

    def get(self, task: dict):
        if not task:
            return
        id = task.get('id')
        url = task.get('url')
        self.taks = task
        if not id or not url:
            self.logger.error(f'No ID or URL in the task: {task}')
            return
        try:
            result = self.get_result_dict(url)
            if result:
                self.queries.update_datas(id, result)
            self.queries.update_last_date(id)
        except Exception as ex:
            self.logger.error(ex)
        finally:
            self.queries.change_status(id, status=True)
            self.close_driver()
            self._del_folder()


    def get_result_dict(self, url: str) -> dict:
        self.driver.get(url)
        self.switch_to_first_window()
        time.sleep(1)
        result = GetKeyStatistic(self.driver.page_source, self.logger).get()
        if result:
            if result.get('link_profile'):
                self.driver.get(result.get('link_profile'))
                time.sleep(1)
                result['profile'] = GetProfileData(self.driver.page_source, self.logger).get()
            if result.get('link_historical_data'):
                if self.load_historical_data_page(result.get('link_historical_data')):
                    time.sleep(1)
                    result['historical_data'] = GetHistoricalData(self.driver.page_source, self.logger).get()
            return result
        return None

    def switch_to_first_window(self):
        tabs = self.driver.window_handles
        if len(tabs) > 1:
            self.driver.switch_to.window(tabs[0])
    
    def load_historical_data_page(self, link: str, count_try: int = 0) -> bool:
        self.driver.get(link)
        try:
            time.sleep(2)
            today_date = datetime.utcnow().strftime("%m/%d/%Y")
            xpath_periods = f'//div[contains(text(), "{today_date}") or contains(text(), " - ")]'
            self.click_element(xpath_periods)
            time.sleep(2)
            table_xpath = "//table[contains(@class, 'freeze-column-w-1')]//tbody/tr"
            rows = self.driver.find_elements(By.XPATH, table_xpath)
            old_count = len(rows)
            try:
                element = self.wait(5, (By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
                self.move_and_click(element)
            except TimeoutException:
                pass
            xpath = '//input[@type="date"]'
            if not self.driver.find_elements(By.XPATH,xpath):
                element_periods = self.driver.find_element(By.XPATH, xpath_periods)
                self.driver.execute_script("arguments[0].removeAttribute('readonly')", element_periods)
                self.click_element(xpath_periods)
                time.sleep(2)
            try:
                self.wait(3, (By.XPATH, xpath))
            except TimeoutException:
                if count_try > 10:
                    raise Exception('Something wrong. Failed to open the date field.')
                return self.load_historical_data_page(link, count_try + 1)
            from_date = '01/01/1980'
            if self.taks.get('from_date', None):
                from_date = self.taks.get('from_date').strftime('%d/%m/%Y')
            self.enter_date(from_date, xpath)
            if self.taks.get('to_date', None):
                time.sleep(1)
                xpath_to = '(//input[@type="date"])[2]'
                to_date = self.taks.get('to_date').strftime('%d/%m/%Y')
                self.enter_date(to_date, xpath_to)
            xpath = "//div[contains(@class, 'cursor-pointer') and contains(@class, 'bg-v2-blue')]"
            self.click_element(xpath)
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda d: len(d.find_elements(By.XPATH, "//table[contains(@class, 'freeze-column-w-1')]//tbody/tr")) != old_count
                )
            except:
                if count_try > 4:
                    self.logger.info(f'Historical data did not update. Link: {link}')
                else:
                    return self.load_historical_data_page(link, count_try + 1)
            return True
        except Exception as ex:
            self.driver.save_screenshot('error.png')
            self.logger.error(ex)
        return False
    
    def enter_date(self, text_date: str, xpath: str):
        date_el = text_date.split('/')
        element_from_date = self.driver.find_element(By.XPATH, xpath)
        element_from_date.send_keys(f"{date_el[0]}/")
        time.sleep(0.3)
        element_from_date.send_keys(Keys.ARROW_RIGHT)
        element_from_date.send_keys(f"{date_el[1]}/")
        time.sleep(0.3)
        element_from_date.send_keys(Keys.ARROW_RIGHT)
        element_from_date.send_keys(f"{date_el[2]}")
        time.sleep(1)

    def click_element(self, xpath: str):
        try:
            element = self.wait(10, (By.XPATH, xpath))
            self.move_and_click(element)
            time.sleep(1)
        except TimeoutException:
            raise Exception(f'There is not xpath: {xpath}')
        
    def move_and_click(self, element: WebElement, text: str = None, y: int = 0, to_click: bool = True):
        self.chain.reset_actions()
        if element is not None:
            self.chain.move_to_element(element)
        if y:
            self.scroll_by(y=y)
        if to_click:
            self.chain.click()
        if text:
            self.chain.send_keys(text)
        self.chain.perform()
        self.chain.reset_actions()
    
    def scroll_by(self, x=0, y=0):
        self.driver.execute_script(f'window.scrollBy({x}, {y});')