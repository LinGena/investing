from bs4 import BeautifulSoup
import json
from logging import Logger as LoggingLogger


class GetKeyStatistic():
    def __init__(self, page_content: str, logger: LoggingLogger = None):
        self.page_content = page_content
        if logger:
            self.logger = logger

    def get(self):
        datas = self.get_dict_from_page_conetnt()
        if not datas:
            return None
        response = {
            'symbol': self.get_symbol(datas),
            'key_stats': self.get_key_stats(datas),
            'overview': datas,
            'link_profile': self.get_link(datas, 'Profile'),
            'link_historical_data': self.get_link(datas, 'Historical Data'),
            'profile': {},
            'historical_data': {}
        }
        return response
    
    def get_link(self, datas: dict, link_name: str) -> str:
        links = datas.get('state',{}).get('pageInfoStore',{}).get('instrumentNavigation',{}).get('overview',{}).get('children')
        for link in links:
            if link.get('name') == link_name:
                return 'https://www.investing.com' + link.get('url')
        return None
    
    def get_symbol(self, datas: dict) -> str:
        return datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('name',{}).get('symbol')

    def get_key_stats(self, datas: dict) -> dict:
        res = {}
        res['name'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('name',{}).get('fullName')
        res['bid'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('bidding',{}).get('bid')
        res['ask'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('bidding',{}).get('ask')
        res['lastClose'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('price',{}).get('lastClose')
        res['open'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('price',{}).get('open')
        res['low'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('price',{}).get('low')
        res['high'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('price',{}).get('high')
        res['fiftyTwoWeekLow'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('price',{}).get('fiftyTwoWeekLow')
        res['fiftyTwoWeekHigh'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('price',{}).get('fiftyTwoWeekHigh')
        res['volume'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('volume',{}).get('_turnover')
        res['volumeAverage'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('volume',{}).get('average')
        res['oneYearReturn'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('fundamental',{}).get('oneYearReturn')
        res['marketCap'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('fundamental',{}).get('marketCapRaw')
        res['sharesOutstanding'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('fundamental',{}).get('sharesOutstanding')
        res['revenue'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('fundamental',{}).get('revenueRaw')
        res['netIncome'] = datas.get('state',{}).get('invproDataStore',{}).get('assetMetricsData',{}).get('proNetIncome')
        res['eps'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('fundamental',{}).get('eps')
        res['earnings_nextReport'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('earnings',{}).get('nextReport')
        res['dividend'] = datas.get('state',{}).get('dividendsSummaryStore',{}).get('equityDividendsSummary',{}).get('annualized_payout')
        res['dividend_yield'] = datas.get('state',{}).get('dividendsSummaryStore',{}).get('equityDividendsSummary',{}).get('dividend_yield')
        res['RSI(14)'] = datas.get('state',{}).get('invproDataStore',{}).get('assetMetricsData',{}).get('RSI(14)')
        res['ratio'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('fundamental',{}).get('ratio')
        res['returnOnAssets'] = datas.get('state',{}).get('invproDataStore',{}).get('assetMetricsData',{}).get('proReturnOnAssets')
        res['returnOnEquity'] = datas.get('state',{}).get('invproDataStore',{}).get('assetMetricsData',{}).get('proReturnOnEquity')
        res['grossProfitMargin'] = datas.get('state',{}).get('invproDataStore',{}).get('assetMetricsData',{}).get('proGrossProfitMargin')
        res['priceBook'] = datas.get('state',{}).get('invproDataStore',{}).get('assetMetricsData',{}).get('proPriceBook')
        res['ebitda'] = datas.get('state',{}).get('invproDataStore',{}).get('assetMetricsData',{}).get('proEbitda')
        res['evEbitda'] = datas.get('state',{}).get('invproDataStore',{}).get('assetMetricsData',{}).get('proEvEbitda')
        res['beta'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('performance',{}).get('beta')
        res['bookValueShare'] = datas.get('state',{}).get('invproDataStore',{}).get('assetMetricsData',{}).get('proBookValueShare')
        res['isin'] = datas.get('state',{}).get('equityStore',{}).get('instrument',{}).get('underlying',{}).get('isin')
        return res

    def get_dict_from_page_conetnt(self) -> dict:
        try:
            soup = BeautifulSoup(self.page_content,'html.parser')
            script_data = soup.find('script',id='__NEXT_DATA__')
            if not script_data:
                raise Exception('There is not tag script with id = __NEXT_DATA__')
            datas = json.loads(script_data.text.strip())
            datas = datas.get('props',{}).get('pageProps',{})
            return datas
        except Exception as ex: 
            if hasattr(self, 'logger'):
                self.logger.error(ex)
            else:
                print(ex)
        return None        