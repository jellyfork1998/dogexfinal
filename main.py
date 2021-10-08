import requests
import pandas as pd
from numerize import numerize
import datetime, time
from datetime import date, timedelta
from bs4 import BeautifulSoup

API_TOKEN = "BSGW5KIFXF6N7GVIZQHIWRFR8IQ8EBMTAH"


def get_coin_data(address):
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "sort": "asc",
        "apikey": API_TOKEN,
    }
    # https: // api.bscscan.com / api?module = account & action = tokentx & address =
    # 0x7bb89460599dbf32ee3aa50798bbceae2a5f7f6a & startblock = 0 & endblock =
    # 2500000 & sort = asc & apikey = YourApiKeyToken

    response = requests.get(url="https://api.bscscan.com/api", params=params)
    response.raise_for_status()
    data = response.json()
    rslt = data['result']
    return rslt


def get_unique_coin_name(allcoinlist):
    all_coin = []
    for i in allcoinlist:
        all_coin.append(i['tokenName'])
    list_set = set(all_coin)
    u_list = (list(list_set))
    return u_list


def get_all_contract_address(allcoinlist):
    all_coin = []
    for i in allcoinlist:
        try:
            coin_unique = {
                "tokenName": i['tokenName'],
                "contractAddress": i['contractAddress']
            }
            all_coin.append(coin_unique)
        except Exception as e:
            pass

    res = list(map(dict, set(tuple(sorted(sub.items())) for sub in all_coin)))
    return res


def remove_space(string):
    return string.replace(" ", "")


def add_sub_individual_coin(rslt, wallet_address, contract_address):
    resultlist = []
    resultDict = {}

    sell_val = 0
    buy_val = 0
    try:
        for x in rslt:

            if x['contractAddress'].lower() == contract_address.lower() and remove_space(
                    x['from']).lower() == remove_space(
                wallet_address).lower():
                # print(f"bval {x['value']}")
                sell_val += float(x['value']) / 1000000000
            elif x['contractAddress'].lower() == contract_address.lower() and remove_space(
                    x['to']).lower() == remove_space(
                wallet_address).lower():
                # print(f"sval {x['value']}")
                buy_val += float(x['value']) / 1000000000

            resultDict = {
                "total_buy": buy_val,
                "total_sell": sell_val,
                "bal_val": buy_val - sell_val,
                "contractAddress": contract_address,
            }
    except IndexError as e:
        pass
    except TypeError as e:
        pass
    except UnboundLocalError as e:
        resultDict = {
            "total_buy": 0,
            "total_sell": 0,
            "bal_val": 0,
            "contractAddress": contract_address,
        }
        resultlist.append(resultDict)

    else:
        resultlist.append(resultDict)

    # print(resultlist)
    return resultlist


def get_coin_current_value(contractaddress, walletaddress):
    params = {
        "module": "account",
        "action": "tokenbalance",
        "contractaddress": contractaddress,
        "address": walletaddress,
        "tag": "latest",
        "apikey": API_TOKEN,
        "tokenPriceUSD": "tokenPriceUSD"
    }

    response = requests.get(url="https://api.bscscan.com/api", params=params)
    response.raise_for_status()
    data = response.json()
    rslt = data['result']
    return rslt


def get_current_price(contractAddress):
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


def get_ticker_list_format(from_coin_Stat, coin_name):
    # usd-0,burn_val-1,total_supply-2,circulating_supply-3,liquidity_val-4,holder_count-5
    tickerlist = []
    statlist = []

    usd = float(from_coin_Stat[0])
    burn_val = float(from_coin_Stat[1])
    total_supply = float(from_coin_Stat[2])
    circulating_supply = float(from_coin_Stat[3])
    liquidity_val = float(from_coin_Stat[4])
    try:
        holder_count = float(from_coin_Stat[5])
    except TypeError as e:
        #holder_count = from_coin_Stat[5]
        holder_count = 1

    coin_price = "%.16f" % usd
    coin_price_string = f"${coin_name} Price:USD$ {coin_price}"

    marketing_cap = f"Total MarketCap: {numerize.numerize(circulating_supply * usd, 2)}"

    burn_perc = (burn_val / total_supply) * 100
    burn_tkn = numerize.numerize(burn_val, 2)
    burn_string = f"Total Burn: {'%.2f' % burn_perc}% ( {burn_tkn} )"

    tot_supply = "{:,.0f}".format(total_supply)
    total_supply_string = f"Total Supply: {tot_supply}"

    circulating_perc = (circulating_supply / total_supply) * 100
    circulating_tkn = numerize.numerize(circulating_supply, 2)
    circulating_string = f"Circulating Supply: {'%.2f' % circulating_perc}% ( {circulating_tkn} )"

    liquidity = f"Pancake Liquidity: {numerize.numerize(liquidity_val, 2)}"
    try:
        holders = f"Total Holders: {'{:,.0f}'.format(holder_count)}"
    except TypeError as e:
        holders = holder_count

    tickerlist = [coin_price_string,
                  marketing_cap,
                  burn_string,
                  total_supply_string,
                  circulating_string,
                  liquidity,
                  holders]

    try:
        hcount = '{:,.0f}'.format(holder_count)
    except TypeError as e:
        hcount = holder_count
        #hcount = "9,131"

    statlist = [coin_price,
                '{:,.0f}'.format(circulating_supply * usd),
                '{:,.0f}'.format(burn_val),
                burn_tkn,
                '%.2f' % float(burn_perc),
                '{:,.0f}'.format(circulating_supply),
                circulating_tkn,
                '%.2f' % float(circulating_perc),
                '{:,.0f}'.format(liquidity_val),
                tot_supply,
                hcount
                ]

    main_list = [tickerlist, statlist]
    return main_list


# def get_coin_geko_api():
#     # get time and subtract 30days and convert to unixtimestamp
#
#     current_date = date.today() + timedelta(1)
#     old_date = current_date - timedelta(30)
#     unix_old = datetime.datetime(old_date.year, old_date.month, old_date.day, 0, 00)
#     unix_cur = datetime.datetime(current_date.year, current_date.month, current_date.day, 0, 00)
#
#     unix_date_current = time.mktime(unix_cur.timetuple())
#     unix_date_old = time.mktime(unix_old.timetuple())
#
#     contract_address = "0xa16976133d3450f78766ecaa1d743621e237e1a5"
#     # ------------start getting data from coin gecko
#
#     params = {
#         "vs_currency": "usd",
#         "from": unix_date_old,
#         "to": unix_date_current
#     }
#     url_data = f"https://api.coingecko.com/api/v3/coins/binance-smart-chain/contract/{contract_address}/market_chart/range"
#     response = requests.get(url=url_data, params=params)
#     response.raise_for_status()
#     data = response.json()
#
#     df = pd.DataFrame(data)
#     return df


def convert_date_from_unx_to_date(df, title, first_String, second_string):
    global unique_date
    price_dic = {}

    a = 0
    for i in df[title]:

        ts = str(i[0])

        if a == 0:
            unique_date = datetime.datetime.fromtimestamp(int(ts[0:10])).strftime('%Y-%m-%d')
            val_data = "%.11f" % float(i[1])
            price_dic = f'{{ {first_String}: "{unique_date}", {second_string}: {val_data}}},'
            a = a + 1
        elif a > 0:
            # print({f"{unique_date} -- {datetime.datetime.fromtimestamp(int(ts[0:10])).strftime('%Y-%m-%d')}"})

            if unique_date != datetime.datetime.fromtimestamp(int(ts[0:10])).strftime('%Y-%m-%d'):
                val_data = "%.11f" % float(i[1])
                unique_date = datetime.datetime.fromtimestamp(int(ts[0:10])).strftime('%Y-%m-%d')
                price_dic += f'{{ {first_String}: "{unique_date}", {second_string}: {val_data}}},'
                a = a + 1

    final_data = price_dic[:-1]
    return final_data


def convert_date_from_unx_to_date_hourly(df, title, first_String, second_string):
    price_dic = ""

    for i in df[title]:
        ts = str(i[0])
        unique_date = datetime.datetime.fromtimestamp(int(ts[0:10])).strftime('%Y-%m-%d')
        val_data = "%.11f" % float(i[1])
        price_dic += f'{{ {first_String}: "{unique_date}", {second_string}: {val_data}}},'

    final_data = price_dic[:-1]

    return final_data


def convert_date_from_unx_to_date_daytrade(df, title, first_String, second_string):
    price_dic = ""

    for i in df[title]:
        ts = str(i[0])
        unique_date = ts[0:10]
        val_data = "%.11f" % float(i[1])
        price_dic += f'{{ {first_String}: {unique_date}, {second_string}: {val_data}}},'

    final_data = price_dic[:-1]

    return final_data
