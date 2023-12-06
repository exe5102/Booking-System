import sqlite3
import json
from datetime import datetime, timezone, timedelta

dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區


def DateControl():
    # MoDays = calendar.monthrange(dt2.year, dt2.month)
    minday = dt2.replace(day=dt2.day + 7)
    #     maxday = dt2.replace(day = dt2.day + 28)
    # except ValueError:
    #     daycont = MoDays[1] - dt2.day
    #     maxday = dt2.replace(month = dt2.month +1, day = 28 - daycont)
    str1 = "".join(dt2.strftime("%Y-%m-%d"))
    str2 = "".join(minday.strftime("%Y-%m-%d"))
    # str3 = ''.join(maxday.strftime("%Y-%m-%d"))
    return str1, str2


def AdminCheck(account, password):  # admin帳密比對
    try:
        with open("pass.json", "r", encoding="UTF-8") as D:
            AdminData = json.load(D)
    except Exception as e:
        print(f"=>檔案讀取失敗，錯誤訊息為{e}")
    else:
        for ch in AdminData:
            if (account, password) == (ch["帳號"], ch["密碼"]):
                return True


def BuildDB():  # 建立訂位資料庫
    conn = sqlite3.connect("booking.db")
    conn.execute(
        """create table if not exists Booking(
            Name    text  not null,
            Phone   char(15)  not null primary key,
            Number  char(15)  not null ,
            Day     char(15)  not null ,
            Time    char(5)  not null
        );"""
    )
    print("=>資料庫已建立")
    conn.close()


def Search(uphone):  # 查詢訂位內容
    try:
        conn = sqlite3.connect("booking.db")
        cursor = conn.execute("select * from Booking where Phone=?", (uphone,))
        data = cursor.fetchall()
        if len(data) > 0:
            for record in data:
                return record
        conn.close()
    except Exception as e:
        print(f"=>資料庫連接或資料表建立失敗，錯誤訊息為{e}")


def AdminDelete(uphone):  # 取消訂位
    try:
        conn = sqlite3.connect("booking.db")
        conn.execute(f"delete from Booking where Phone='{uphone}'")
        conn.commit()
        conn.close()
        return "已取消訂位"
    except Exception as e:
        print(f"=>資料庫連接或資料表建立失敗，錯誤訊息為{e}")


def SearchAll():  # 列出所有資料
    conn = sqlite3.connect("booking.db")
    cursor = conn.execute(" select * from Booking ")
    data = cursor.fetchall()
    return data
