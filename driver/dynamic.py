import os
import zipfile
import uuid
import shutil
import time
from pyvirtualdisplay import Display
import undetected_chromedriver as uc_webdriver
from driver.proxy_ext import load_proxy
from config.settings import settings
from utils.logger import Logger


class UndetectedDriver():
    def __init__(self, first_create):
        self.first_create = first_create
        self.logger = Logger().get_logger(__name__)
        self.open_display()
        self.create_folder_path()
        self._set_chromeoptions()
        self.driver = self._create_driver()

    def __del__(self):
        self.close_driver()
        self._del_folder()

    def open_display(self):
        self._display = Display(visible=False, size=(1920, 1080))
        self._display.start()
        
    def create_folder_path(self):
        self.folder_path = f"chrome_data/temp_{uuid.uuid4().hex}"
        os.makedirs(self.folder_path, exist_ok=True)

    def _create_extensions(self) -> str:
        extensions = []
        proxy_extension_path = load_proxy(self.folder_path)
        extensions.append(proxy_extension_path)
        adblock_folder = "adblock_ext"
        adblock_zip = "driver/adblock.zip"
        if not os.path.exists(adblock_folder):
            if os.path.exists(adblock_zip):
                with zipfile.ZipFile(adblock_zip, "r") as zip_ref:
                    zip_ref.extractall(adblock_folder)
        if os.path.exists(adblock_folder):
            extensions.append(adblock_folder)
        return ','.join(extensions)

    def _set_chromeoptions(self):
        self.__options = uc_webdriver.ChromeOptions()
        self.__options.add_argument(f"--load-extension={self._create_extensions()}")
        self.__options.add_argument("--lang=en-US")
        self.__options.add_argument("--accept-lang=en-US,en;q=0.9")
        self.__options.add_argument('--ignore-ssl-errors=yes')
        self.__options.add_argument('--ignore-certificate-errors')
        self.__options.add_argument('--start-maximized')
        self.__options.add_argument('--no-sandbox')
        self.__options.add_argument('--disable-dev-shm-usage')
        self.__options.add_argument('--disable-setuid-sandbox')
        self.__options.add_argument('--disable-gpu')
        self.__options.add_argument('--disable-software-rasterizer')
        self.__options.add_argument("--disable-notifications")
        self.__options.add_argument("--disable-popup-blocking")
        self.__options.add_argument("--disable-features=WebRtcHideLocalIpsWithMdns")
        self.__options.add_experimental_option('prefs', {
            'enable_do_not_track': True
        })
        preferences = {
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False
        }
        self.__options.add_experimental_option("prefs", preferences)

    def _create_driver(self):
        if self.first_create:
            driver = uc_webdriver.Chrome(version_main=int(settings.driver.chrome_version),
                                        user_data_dir=self.folder_path,
                                        options=self.__options)
        else:
            driver = uc_webdriver.Chrome(version_main=int(settings.driver.chrome_version),
                                        user_data_dir=self.folder_path,
                                        options=self.__options,
                                        user_multi_procs=True)
        return driver
    
    def close_driver(self):
        try:
            self.driver.close()
        except:
            pass
        try:
            self.driver.quit()
        except:
            pass
        try:
            self._display.stop()
        except:
            pass 

    def _del_folder(self):
        if hasattr(self,'folder_path') and os.path.exists(self.folder_path):
            try:
                time.sleep(1)
                shutil.rmtree(self.folder_path)
            except Exception as ex:
                self.logger.debug(ex)