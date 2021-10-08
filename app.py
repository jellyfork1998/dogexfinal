import csv
from datetime import datetime, time

import requests
from flask import Flask, render_template, request, url_for, jsonify
from numerize import numerize
import os
from flask_sqlalchemy import SQLAlchemy
from main import get_coin_data, get_all_contract_address, add_sub_individual_coin, \
    get_coin_current_value, get_current_price, get_ticker_list_format,  \
    convert_date_from_unx_to_date_daytrade
from coinstat import ticker_get_ready_ticker_data, ticker_get_current_time, get_top_holders_list

import sqlite3

COIN_ADDRESS = "0xf57fcAB4E5B76fc49917f6AC11eac27E222ca111"
COIN_NAME = "DogeX"  # dogeXURI
# ur="postgres://lgmgpglumbaozp:373d565c4be1b50f3c70802a3a5c4a5f5cb933413d8d6a4fa93cab2b6e64742c@ec2-107-20-24-247.compute-1.amazonaws.com:5432/d6pfnn4i2t55vm"
# urrev1=postgres://bwgkkvahgxbepc:58b40579176560f51d462b430b273d3193478ae6f0edded6194f106d5a9c7b21@ec2-23-20-124-77.compute-1.amazonaws.com:5432/da3afpub2acupl
# dogexpaid = postgres://u7gf3srkklvg7d:p2078677b9bf8f49d7c75016cc1fd522e65662eab12170192388baf71cf8bbaaa@ec2-3-215-123-6.compute-1.amazonaws.com:5432/d850s56b8vo3lo
# uri = os.getenv("DATABASE_URL")  # or other relevant config var
# if uri.startswith("postgres://"):
#      uri = uri.replace("postgres://", "postgresql://", 1)

# for heroku database connection
# ---------------------------------------------------------------------------------------
#uri = os.getenv("HEROKU_POSTGRESQL_WHITE_URL")  # or other relevant config var
#if uri.startswith("postgres://"):
#  uri = uri.replace("postgres://", "postgresql://", 1)
#trial=postgres://tkulhtivowimmt:67dc95fdb97225eb208332b2a6a5dd5c71a4dde2f529a93819094b2b50efad4f@ec2-34-197-135-44.compute-1.amazonaws.com:5432/d262010vvoqtj8
# -----------------------------------------------------------------------
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = uri    # need to uncomment when connect to database
#
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dogexdb.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.secret_key=os.environ.get('SECRETKEY')
db = SQLAlchemy(app)

# ----
result_list = []


##CREATE TABLE AND GETTING DATA FROM DATABASE
# class TopHolder(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     holderName = db.Column(db.String(250), unique=True, nullable=False)
#     holder_contract_address = db.Column(db.String(250), unique=True,  nullable=False)
#     coin_val = db.Column(db.String(250), nullable=False)
#     time_captured_holder=db.Column(db.String(100), nullable=False)


class TickerInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usd = db.Column(db.String(250), unique=True, nullable=False)
    burn_val = db.Column(db.String(250), unique=True, nullable=False)
    total_supply = db.Column(db.String(250), nullable=False)
    circulating_supply = db.Column(db.String(100), nullable=False)
    liquidity_val = db.Column(db.String(100), nullable=False)
    holder_count = db.Column(db.String(100), nullable=False)
    time_captured_tick = db.Column(db.String(100), nullable=False)


db.create_all()


# function to extract top holders data from db to list
# def extract_topholders_from_db_to_list():
#     tholder=[]
#     db_topholder = db.session.query(TopHolder).all()

#     for i in db_topholder:
#         tholder.append(i.coin_val)
#     tholder.append(db_topholder[0].time_captured_holder)
#     return tholder


# function to read first data from database ticker_info
def extract_gendata_from_db_to_list():
    gendata_info = []
    db_tickerinfo = db.session.query(TickerInfo).first()
    gendata_info.append(db_tickerinfo.usd)
    gendata_info.append(db_tickerinfo.burn_val)
    gendata_info.append(db_tickerinfo.total_supply)
    gendata_info.append(db_tickerinfo.circulating_supply)
    gendata_info.append(db_tickerinfo.liquidity_val)
    gendata_info.append(db_tickerinfo.holder_count)
    gendata_info.append(db_tickerinfo.time_captured_tick)
    return gendata_info


def update_data_ticker_info(usd, burn_val, total_supply, circulating_supply, liquidity_val, holder_count,
                            time_captured_tick):
    coin_id = 1
    ticker_update = TickerInfo.query.get(coin_id)
    ticker_update.usd = usd
    ticker_update.burn_val = burn_val
    ticker_update.total_supply = total_supply
    ticker_update.circulating_supply = circulating_supply
    ticker_update.liquidity_val = liquidity_val

    # ticker_update.holder_count = holder_count
    # ticker_update.holder_count = "1"
    ticker_update.time_captured_tick = str(time_captured_tick)
    db.session.commit()


def get_api_data():
    gold_hour = []
    headers = {
        "key": "jdi38j92hdor9"
    }
    response = requests.get("https://get-taxes-api-p6uoq.ondigitalocean.app/get/", headers=headers)
    resp = requests.get(
        "https://current-limits-api-dsjq9.ondigitalocean.app/get/?address=0xbD6B5A591964F2ecbd521c98C4002f18034Ee7c0",
        headers=headers)
    gold_hour.append(response.json())
    gold_hour.append(resp.json())
    return gold_hour


# def update_data_to_topholder(coin_val):
#     db_topholder = db.session.query(TopHolder).all()
#     a=0
#     for i in db_topholder:
#         i.coin_val=coin_val[a]
#         i.time_captured_holder=coin_val[5]
#         a+=1
#     db.session.commit()

def add_gendata():
    new_book = TickerInfo(id=1, usd="0.0000454", burn_val="0.0000054875", total_supply="45000000000",
                          circulating_supply="1213233464", liquidity_val="231241545454",
                          holder_count="21541544", time_captured_tick="12113144")
    db.session.add(new_book)
    db.session.commit()


# def add_tickerdata():
#    holderone=TopHolder(id=1,holderName="Pancakewap",holder_contract_address= "contractadd1", coin_val="43433434354545",time_captured_holder="454545454")
#    holdertwo = TopHolder(id=2, holderName="dxdeveloper1", holder_contract_address="contractadd2",
#                          coin_val="43433434354545",time_captured_holder="454545454")
#    holderthree = TopHolder(id=3, holderName="Pancakewap3", holder_contract_address="contractadd3",
#                          coin_val="43433434354545",time_captured_holder="454545454")
#    holderfour = TopHolder(id=4, holderName="Pancakewap4", holder_contract_address="contractadd4",
#                          coin_val="43433434354545",time_captured_holder="454545454")
#    holderfive = TopHolder(id=5, holderName="Pancakewap5", holder_contract_address="contractadd5",
#                          coin_val="43433434354545",time_captured_holder="454545454")
#    db.session.add(holderone)
#    db.session.add(holdertwo)
#    db.session.add(holderthree)
#    db.session.add(holderfour)
#    db.session.add(holderfive)

#    db.session.commit()


# add_topholders()
# print(extract_gendata_from_db_to_list())
# add_tickerdata()


# ---------------logic--------------------------------
def ticker_time_comparison():
    final_result = []
    current_time = int(datetime.now().timestamp())
    holder = 0  # temperory variable for holder
    try:
        db_latest_ticker_data = extract_gendata_from_db_to_list()  # extract from data base
        # print(db_latest_ticker_data)
        # print(f" {int(db_latest_ticker_data[6])}")
        # print(f" {int(current_time )}")
        # print(f" {current_time-int(db_latest_ticker_data[6])}")
        if (int(current_time) - int(db_latest_ticker_data[6])) > 60:
            final_result = ticker_get_ready_ticker_data()  # from api call


            # update database
            # update_data_ticker_info(final_result[0]['usd'], final_result[0]['burn_val'],
            #                         final_result[0]['total_supply'],
            #                         final_result[0]['circulating_supply'], final_result[0]['liquidity_val'],
            #                         final_result[0]['holders'], str(current_time))

            update_data_ticker_info(final_result[0]['usd'], final_result[0]['burn_val'],
                                    final_result[0]['total_supply'],
                                    final_result[0]['circulating_supply'], final_result[0]['liquidity_val'],
                                    db_latest_ticker_data[5], str(current_time))

            final_result = [final_result[0]['usd'], final_result[0]['burn_val'], final_result[0]['total_supply'],
                            final_result[0]['circulating_supply'], final_result[0]['liquidity_val'],
                            db_latest_ticker_data[5], current_time]


            #print(f"try {final_result}")
            return final_result
        else:
            final_result = db_latest_ticker_data
            #print(f"db {final_result}")
            return final_result

    except Exception as e:
        final_result = ticker_get_ready_ticker_data()

        final_result = [final_result[0]['usd'], final_result[0]['burn_val'], final_result[0]['total_supply'],
                        final_result[0]['circulating_supply'], final_result[0]['liquidity_val'],
                        holder, current_time]
        return final_result


# def pie_data_comparison():
#     final_result = []
#     current_time = ticker_get_current_time()
#     try:
#         db_latest_holder_data = extract_topholders_from_db_to_list()
#         if (current_time - int(db_latest_holder_data[5])) > 60:
#             final_result = get_top_holders_list()
#             final_result.append(str(current_time))
#             update_data_to_topholder(final_result)
#             return final_result
#         else:
#             final_result = db_latest_holder_data
#             return final_result
#     except Exception as e:
#         final_result = get_top_holders_list()
#         final_result.append(current_time)
#         return final_result


# -----------------------------------------------------


c_address = COIN_ADDRESS
coin_list_rows = []

rslt = []  # all coin name in list
rslt_dic = {}  # all coin name with contract address in dictionary
from_coin_Stat = ticker_time_comparison()

# ------------------------------------------------------------


total_token = 0
total_purchased = 0
total_sold = 0
bal_token = 0
startno = ""
tickerlist = []
statlist = []
walletAddress = ""
top_holders = []
# ----for line graph
# df = get_coin_geko_api()
# volume_list = convert_date_from_unx_to_date_daytrade(df, 'total_volumes', 'time', 'value')
# price_list = convert_date_from_unx_to_date_daytrade(df, 'prices', 'time', 'value')


#     price_date_list += f"'{i}',"
# price_date_list=price_date_list[:-1]
# for i in p_list[1]:
#     price_list += i+","
# price_list=price_list[:-1]


# volume_list = convert_date_from_unx_to_date(df, 'total_volumes')
# market_list = convert_date_from_unx_to_date(df, 'market_caps')
# dat_list = []


@app.route('/')
def index():
    global total_token
    total_token = 0

    global total_purchased
    total_purchased = 0

    global total_sold
    total_sold = 0

    global bal_token
    bal_token = 0

    global startno
    startno = ""

    gold_hour = get_api_data()
    gd = {"gold_buy": gold_hour[0]['buy'],
          "gold_sell": gold_hour[0]['sell'],
          "gold_sell_limit": gold_hour[1]['sellLimit'],
          "gold_time_limit": gold_hour[1]['timeLimit']}

    global from_coin_Stat
    from_coin_Stat = ticker_time_comparison()
    global result_list
    result_list = get_ticker_list_format(from_coin_Stat, COIN_NAME)

    return render_template("index.html", total_token=total_token, total_purchased=total_purchased,
                           total_sold=total_sold, bal_token=bal_token, alertmsgbox=startno, tickerlist=result_list[0],
                           statlist=result_list[1], gold_json=gd)


# ------------------pie chart and ticker ------------------------
# global top_holders
# top_holders=pie_data_comparison()
# return render_template("index.html", total_token=total_token, total_purchased=total_purchased,
#                        total_sold=total_sold, bal_token=bal_token, alertmsgbox=startno, tickerlist=result_list[0],
#                        statlist=result_list[1], volume_list=volume_list, price_list=price_list,
#                        top_holders=top_holders)


@app.route('/handle_data', methods=['POST'])
def handle_data():
    st = ""
    val_Zero = 0

    wallet_address = request.form['walletAddress']
    # print(wallet_address)
    # print(COIN_ADDRESS)
    all_coin = get_coin_data(wallet_address)

    # global rslt
    # rslt = get_unique_coin_name(all_coin)
    # print(f" rslt {rslt}") # coin name

    global rslt_dic
    rslt_dic = get_all_contract_address(all_coin)

    global top_holders
    # top_holders = pie_data_time_comparison()

    global result_list

    gold_hour = get_api_data()
    gd = {"gold_buy": gold_hour[0]['buy'],
          "gold_sell": gold_hour[0]['sell'],
          "gold_sell_limit": gold_hour[1]['sellLimit'],
          "gold_time_limit": gold_hour[1]['timeLimit']}

    try:
        ix = add_sub_individual_coin(all_coin, wallet_address, COIN_ADDRESS)
    except IndexError as e:
        curr_price = 0
        total_token_value = 0
        total_purchased_value = 0
        total_bal_value = 0

        total_token = 0
        total_purchased = 0
        bal_token = 0
        total_sold = 0

    else:

        try:
            global total_purchased
            total_purchased = ix[0]['total_buy']

            global total_sold
            total_sold = ix[0]['total_sell']

            global total_token
            total_token = round(float(get_coin_current_value(COIN_ADDRESS, wallet_address)) / 1000000000,
                                4)

            global bal_token
            bal_token = total_token - ix[0]['bal_val']

            global startno
            startno = ""
            if bal_token < 0 and total_sold == 0:
                bal_token = bal_token * -1
                st = "Probably you have sold all your reflections"
            # print(type(total_sold))
            # print(type(total_purchased))
            # ----/change sold value to diamond hands----------
            if total_sold == 0 and total_purchased == 0:
                val_Zero = 1
                total_sold = 0
            elif total_sold == 0 and total_purchased > 0:
                val_Zero = 0
                total_sold = "Sold None 💎🤲"
            else:
                total_sold = f"{round(total_sold, 2)}({numerize.numerize(total_sold, 2)})"

            curr_price = float(get_current_price(COIN_ADDRESS))
            total_token_value = total_token * curr_price
            total_purchased_value = total_purchased * curr_price
            total_bal_value = bal_token * curr_price
            # result_list = get_ticker_list_format(from_coin_Stat, COIN_NAME)
            if val_Zero == 0:
                total_token = f"{round(total_token, 2)} ({numerize.numerize(total_token, 2)})  (USD:${round(total_token_value, 2)})"
                total_purchased = f"{round(total_purchased, 2)} ({numerize.numerize(total_purchased, 2)} ) "
                bal_token = f"{round(bal_token, 2)} ({numerize.numerize(bal_token, 2)}) (USD:${round(total_bal_value, 2)}) "
            elif val_Zero == 1:
                total_token = 0
                total_purchased = 0
                bal_token = 0
        except KeyError as e:
            curr_price = 0
            total_token_value = 0
            total_purchased_value = 0
            total_bal_value = 0

            total_token = 0
            total_purchased = 0
            bal_token = 0
            total_sold = 0

        except TypeError as e:
            total_token = 0
            total_purchased = 0
            bal_token = 0
            total_sold = 0

        except IndexError as e:
            total_token = 0
            total_purchased = 0
            bal_token = 0
            total_sold = 0
    # -----------------including pie and tickerlist -----------------------------
    # return render_template("index.html", total_token=total_token, total_purchased=total_purchased,
    #                        total_sold=total_sold, bal_token=bal_token, remarks=st,
    #                        contract_address=wallet_address, alertmsgbox=startno, tickerlist=result_list[0],
    #                        statlist=result_list[1], volume_list=volume_list, price_list=price_list,top_holders=top_holders)

    return render_template("index.html", total_token=total_token, total_purchased=total_purchased,
                           total_sold=total_sold, bal_token=bal_token, remarks=st,
                           contract_address=wallet_address, alertmsgbox=startno, tickerlist=result_list[0],
                           statlist=result_list[1], gold_json=gd)


@app.route('/suggestions')
def suggestions():
    gold_hour = get_api_data()
    gd = {"gold_buy": gold_hour[0]['buy'],
          "gold_sell": gold_hour[0]['sell'],
          "gold_sell_limit": gold_hour[1]['sellLimit'],
          "gold_time_limit": gold_hour[1]['timeLimit']}
    return jsonify(gd)


if __name__ == "__main__":
    app.run(debug=True)
