from bs4 import BeautifulSoup
from logging import Logger as LoggingLogger
import pandas as pd
import re

class GetHistoricalData():
    def __init__(self, page_content: str, logger: LoggingLogger = None):
        self.page_content = page_content
        if logger:
            self.logger = logger

    def get(self) -> dict:
        try:
            soup = BeautifulSoup(self.page_content,'html.parser')
            rows = soup.select("table.freeze-column-w-1 tbody tr")
            data = []
            for row in rows:
                cols = row.find_all("td")
                if cols:
                    raw_date = cols[0].find("time").text.strip() if cols[0].find("time") else cols[0].text.strip()
                    try:
                        date = pd.to_datetime(raw_date, format="%b %d, %Y").strftime("%Y-%m-%d")
                    except:
                        date = raw_date
                    price = cols[1].text.strip()
                    open_price = cols[2].text.strip()
                    high = cols[3].text.strip()
                    low = cols[4].text.strip()
                    volume = cols[5].text.strip()
                    change = cols[6].text.strip() if len(cols) > 6 else "N/A"
                    try:
                        if "K" in volume:
                            volume = float(volume.replace("K", "").replace(",", "")) * 1_000
                        elif "M" in volume:
                            volume = float(volume.replace("M", "").replace(",", "")) * 1_000_000
                        elif "B" in volume:
                            volume = float(volume.replace("B", "").replace(",", "")) * 1_000_000_000
                        else:
                            volume = float(volume.replace(",", ""))
                    except:
                        volume = None

                    change = cols[6].text.strip() if len(cols) > 6 else "N/A"
                    try:
                        change = float(re.sub(r"[%+]", "", change))
                    except:
                        change = None
                    data.append({
                        "Date": date,
                        "Price": price,
                        "Open": open_price,
                        "High": high,
                        "Low": low,
                        "Volume": volume,
                        "Change %": change
                    })
            return data
        except Exception as ex: 
            if hasattr(self, 'logger'):
                self.logger.error(ex)
            else:
                print(ex)
        return None  