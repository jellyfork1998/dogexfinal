from datetime import datetime
import requests
from bs4 import BeautifulSoup
from main import get_coin_current_value

# -------------COIN PARAMETERS


API_TOKEN = "17J2JX7UV6AUSJ4YU7FZK7Z63GY1FS6SWZ"
CONTRACT_ADDRESS = "0xf57fcAB4E5B76fc49917f6AC11eac27E222ca111"
LIQUID_POOL = "0xbd350508758cdf1b19e5c0344e1704015cdef8be"
BURN_ADDRESS = "0x000000000000000000000000000000000000dead"
DIVIDE_VALUE = 1000000000
# -----------------------------------------------------------------
# -----------for pie chart data
TOP_WALLETS = [["pancakeswap", "PancakeSwap Liquidity", "0xa915fa6b335e12e8625933c0974c6f0302469dee"],
               ["dxlocker", "DxLocker", "0x2d045410f002a95efcee67759a92518fa3fce677"],
               ["reserve", "Reserve Supply", "0xfc8265fb59fc38978a3c28c07572289a8a5c01ab"],
               ["developer_wallet", "Developer Wallet", "0x3ade241eded91fe0f10cdb93a7295c6469220b2b"]]
TOTAL_SUPPLY = 1000000000000000
# ----------------------------------------------------------------

ticker_dic = []


def ticker_get_coin_current_value(contractaddress, walletaddress):
    params = {
        "module": "account",
        "action": "tokenbalance",
        "contractaddress": contractaddress,
        "address": walletaddress,
        "tag": "latest",
        "apikey": API_TOKEN,

    }
    #print(contractaddress)
    #print("one")
    rslt = 0
    response = requests.get(url="https://api.bscscan.com/api", params=params)
    response.raise_for_status()
    data = response.json()
    #print(data)
    if data['result'] != '0':
        try:
            rslt = int(float(data['result'])) / DIVIDE_VALUE
            #print(f"try {rslt}")
            return rslt

        except Exception as e:
            #print(f"error{rslt}")
            rslt = int(data['result']) / DIVIDE_VALUE
            return rslt
    else:
        #print(f"zero{rslt}")
        return rslt


#ticker_get_coin_current_value
# for pancake api
# def ticker_get_current_price(contractAddress):
#     response = requests.get(url="https://api.pancakeswap.info/api/v2/tokens/" + contractAddress)
#     response.raise_for_status()
#     data = response.json()
#     usdPrice = data['data']['price']
#      print(usdPrice)
#     return usdPrice


def ticker_get_current_price(contractAddress):
    params = {

        "sellToken": contractAddress,
        "buyToken": "BUSD",
        "sellAmount": 1000000000000000000
    }
    response = requests.get(url="https://bsc.api.0x.org/swap/v1/price", params=params)
    response.raise_for_status()
    data = response.json()
    usdPrice = data['price']
    return usdPrice


def ticker_get_holder_number():
    response = requests.get(f"https://bscscan.com/token/{CONTRACT_ADDRESS}#balances")
    yc_web_page = response.text
    soup = BeautifulSoup(yc_web_page, "html.parser")
    articles = soup.find("div", {"id": "ContentPlaceHolder1_tr_tokenHolders"})
    try:
        final_result = articles.find_all("div", class_="mr-3")[0].text.split(" ")[0].replace(",", "")
    except AttributeError as e:
        final_result = "9,131"
    else:
        return final_result


def ticker_get_current_time():
    current_time = datetime.now()
    final_time = int(current_time.strftime("%d%m%Y%H%M%S"))
    return final_time


def ticker_get_total_supply():
    params = {
        "module": "stats",
        "action": "tokensupply",
        "contractaddress": CONTRACT_ADDRESS,
        "apikey": API_TOKEN

    }

    response = requests.get(url="https://api.bscscan.com/api", params=params)
    response.raise_for_status()
    data = response.json()
    total_supply = int(data['result']) / DIVIDE_VALUE
    return total_supply


def ticker_get_ready_ticker_data():
    result_dic_list = []
    usd = ticker_get_current_price(CONTRACT_ADDRESS)
    burn_val = ticker_get_coin_current_value(CONTRACT_ADDRESS, BURN_ADDRESS)
    total_supply = ticker_get_total_supply()
    circulating_supply = total_supply - burn_val
    liquidity_val = ticker_get_coin_current_value(CONTRACT_ADDRESS, LIQUID_POOL)
    try:
        holders = ticker_get_holder_number().replace("\n", "")
    except AttributeError as e:
        holders = ticker_get_holder_number()
    current_time = ticker_get_current_time()
    result_dic = {
        "usd": usd,
        "burn_val": burn_val,
        "total_supply": total_supply,
        "circulating_supply": circulating_supply,
        "liquidity_val": liquidity_val,
        "holders": holders,
        "time_captured": current_time

    }
    result_dic_list.append(result_dic)
    return result_dic_list


# def ticker_create_csv():
#     rt = ticker_get_ready_ticker_data()
#     df = pd.DataFrame.from_dict(rt)
#     df.to_csv(r'gens.csv', index=False, header=True)


# def ticker_read_from_gen_csv():
#     try:
#         data = pd.read_csv("gens.csv")
#     except Exception as e:
#         ticker_create_csv()
#         data = pd.read_csv("gens.csv")
#         return data
#     else:
#         return data


# ------------------piechart data-----
# region
def get_top_holders_list():
    total_all = 0
    top_holders = []

    for i in TOP_WALLETS:
        ne_val = int(get_coin_current_value(CONTRACT_ADDRESS, i[2])) / 1000000000
        total_all += ne_val
        top_holders.append(ne_val)
    bal_val = TOTAL_SUPPLY - total_all
    top_holders.append(bal_val)
    top_holders.append(ticker_get_current_time())
    return top_holders


def pie_data_from_dic_to_list(rstl_dic):
    top_holder_list = [rstl_dic['pancakeswap'][0], rstl_dic['dxlocker'][0], rstl_dic['reserve'][0],
                       rstl_dic['developer_wallet'][0], rstl_dic['other_holder'][0],
                       rstl_dic['other_holder'][0]]
    return top_holder_list


# def pie_data_read_from_topholder_csv():
#     try:
#         data = pd.read_csv("topholder.csv")
#
#     except FileNotFoundError as e:
#         create_topholders_csv()
#         data = pd.read_csv("topholder.csv")
#         return data
#     else:
#         return data


# def create_topholders_csv():
#     rt = get_top_holders_list()
#     rt_dic = [{
#         "pancakeswap": rt[0],
#         "dxlocker": rt[1],
#         "reserve": rt[2],
#         "developer_wallet": rt[3],
#         "other_holder": rt[4],
#         "time_captured": rt[5]
#     }]
#     df = pd.DataFrame.from_dict(rt_dic)
#     df.to_csv(r'topholder.csv', index=False, header=True)


# def ticker_data_comparison():
#     final_result = []
#     current_time = ticker_get_current_time()
#     db_latest_holder_data = extract_topholders_from_db_to_list()
#     if (current_time - db_latest_holder_data.time_captured_tick) > 60:
#         final_result = get_top_holders_list()
#         update_data_ticker_info(final_result[0], final_result[1], final_result[2], final_result[3], final_result[4],
#                                 final_result[5], current_time)
#         return final_result
#     else:
#         final_result = db_latest_ticker_data
#         return final_result



