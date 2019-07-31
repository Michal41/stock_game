from bs4 import BeautifulSoup
import requests


class Stock:
    @staticmethod
    def find_stock_prices(sektor):
        r = requests.get(f"https://www.bankier.pl/gielda/notowania/akcje?sector={sektor}")
        soup = BeautifulSoup(r.text, 'html.parser')
        result_list = soup.find_all("tr")
        stock_list = {}
        for result in result_list[1:-1]:
            company_name = (result.contents[1].text).replace("\n", "")
            stock_price = (result.contents[3].text).replace(",", ".")
            stock_list[company_name] = stock_price
        return stock_list
    @staticmethod
    def stock_list():
        stock_list = Stock.find_stock_prices("541")
        stock_list.update(**Stock.find_stock_prices("411"), **Stock.find_stock_prices("632"), **Stock.find_stock_prices("631"))
        return stock_list