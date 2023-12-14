import sqlite3
import json
from datetime import datetime, timezone, timedelta

DB_PATH = "booking.db"
Pass_Data = "pass.json"
room = {"one": 0, "two": 0, "four": 0}


def DateControl() -> tuple:
    """
    時間讀取

    將時區轉換為東8區
    新增可預約日期起點

    timestr 可預約日期格式轉換為字串
    nowtm 現在日期格式轉換為字串
    """
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區
    minday = dt2.replace(day=dt2.day + 7)
    timestr = "".join(minday.strftime("%Y-%m-%d"))
    nowtm = "".join(dt2.strftime("%Y-%m-%d"))
    return timestr, nowtm


def check(act: str, pw: str) -> bool:
    """json.load() 讀取 JSON 檔案，判斷密碼是否正確"""
    try:
        with open(Pass_Data, "r", encoding="UTF-8") as D:
            UserData = json.load(D)
    except FileNotFoundError:  # 找不到對象檔案
        print("找不到檔案")
    except IOError:  # 檔案讀取錯誤
        print("讀取失敗")
    except (EOFError, KeyboardInterrupt):  # 例: ctrl + c
        print("使用者中斷程式")
    except BaseException:
        print("發生預期外的錯誤")
    for ch in UserData:
        return True if (act, pw) == (ch["帳號"], ch["密碼"]) else False


def DBcreate() -> None:
    """建立資料表

    iid 自動累加 整數 主索引
    Name 文字 不可為空
    Day 文字 不可為空
    Phone 文字 不可為空 唯一性
    Roomtype 整數 不可為空

    """
    try:
        conn = sqlite3.connect(DB_PATH)  # 連接資料庫
        cursor = conn.cursor()  # 建立cursor物件
        cursor.execute(
            """create table if not exists Booking(
                iid INTEGER PRIMARY KEY autoincrement,
                Name TEXT NOT NULL,
                Day TEXT NOT NULL,
                Phone TEXT UNIQUE NOT NULL,
                Roomtype INTEGER NOT NULL
                );"""
        )
        conn.close()
    except sqlite3.Error as error:
        print(f"執行 INSERT 操作時發生錯誤：{error}")
    else:
        print("=>資料庫已建立")


def DBAll() -> tuple:
    """抓取資料庫所有資料"""
    try:
        conn = sqlite3.connect(DB_PATH)  # 連接資料庫
        cursor = conn.cursor()  # 建立cursor物件
        cursor.execute("SELECT * FROM Booking")
        data = cursor.fetchall()
        conn.close()
        return data
    except sqlite3.Error as error:
        print(f"執行 SELECT 操作時發生錯誤：{error}")


def DBnew(name: str, day: str, phone: str, rt: int) -> bool:
    """使用者在資料庫中新增資料"""
    try:
        conn = sqlite3.connect(DB_PATH)  # 連接資料庫
        cursor = conn.cursor()  # 建立cursor物件
        cursor.execute(
            """
                INSERT INTO Booking (Name, Day, Phone, Roomtype)
                SELECT ?, ?, ?, ? WHERE NOT EXISTS (
                    SELECT 1 FROM Booking WHERE Phone=?);
            """,
            (name, day, phone, rt, phone),
        )
        print(f"=>異動 {cursor.rowcount} 筆記錄")
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as error:
        print(f"執行 SELECT 操作時發生錯誤：{error}")
        return False


def DBedit(mname: str, Day: str, uphone: str, rt: int) -> tuple:
    """修改資料庫指定資料"""
    try:
        conn = sqlite3.connect(DB_PATH)  # 連接資料庫
        cursor = conn.cursor()  # 建立cursor物件
        cursor.execute(
            "UPDATE Booking SET Day=?, mname=?, Roomtype=? WHERE Phone=?;",
            (Day, mname, rt, uphone),
        )
        print(f"=>異動 {cursor.rowcount} 筆記錄")
        conn.commit()
        conn.close()
        return DBsearch(uphone)
    except sqlite3.Error as error:
        print(f"執行 SELECT 操作時發生錯誤：{error}")


def DBsearch(uphone: tuple) -> tuple:
    """查詢資料庫指定資料，以電話搜尋"""
    try:
        conn = sqlite3.connect(DB_PATH)  # 連接資料庫
        cursor = conn.cursor()  # 建立cursor物件
        cursor.execute("SELECT * FROM Booking WHERE Phone=?", (uphone,))
        DBdata = cursor.fetchall()  # 抓取所有資料
        if len(DBdata) > 0:  # 判斷有無資料
            for record in DBdata:
                return record
        else:
            print("查無資料")
        conn.close()
    except sqlite3.Error as error:
        print(f"執行 SELECT 操作時發生錯誤：{error}")


def DBTableDelete() -> None:
    """刪除資料表所有資料"""
    try:
        conn = sqlite3.connect(DB_PATH)  # 連接資料庫
        cursor = conn.cursor()  # 建立cursor物件
        cursor.execute("DELETE FROM  Booking")
        print(f"=>異動 {cursor.rowcount} 筆記錄")
        conn.commit()
        conn.close()
    except sqlite3.Error as error:
        print(f"執行 DELETE 操作時發生錯誤：{error}")


def DeleteData(uphone: str) -> None:
    """刪除資料庫中的指定資料"""
    try:
        conn = sqlite3.connect(DB_PATH)  # 連接資料庫
        cursor = conn.cursor()  # 建立cursor物件
        cursor.execute("delete from Booking where Phone=?", (uphone,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"=>資料庫連接或資料表建立失敗，錯誤訊息為{e}")


# def roomlimint():
#     if room["one"]
