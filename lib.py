import sqlite3
import json
from datetime import datetime, timezone, timedelta

DB_PATH = "booking.db"
Pass_Data = "pass.json"


def DateControl() -> str:
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區
    minday = dt2.replace(day=dt2.day + 7)
    timestr = "".join(minday.strftime("%Y-%m-%d"))
    nowtm = "".join(dt2.strftime("%Y-%m-%d"))
    return timestr, nowtm


def check(act: str, pw: str) -> bool:  # 完成
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
        if (act, pw) == (ch["帳號"], ch["密碼"]):
            return True


def DBcreate() -> None:  # 完成
    """建立資料表"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(  # 建立表 Booking
            """create table if not exists Booking(
                iid INTEGER PRIMARY KEY autoincrement,
                Name TEXT NOT NULL,
                Day TEXT NOT NULL,
                Phone TEXT UNIQUE NOT NULL,
                Headcount INTEGER NOT NULL
                );"""
        )
        conn.close()
    except sqlite3.Error as error:
        print(f"執行 INSERT 操作時發生錯誤：{error}")
    else:
        print("=>資料庫已建立")


def DBAll() -> list:
    """抓取資料庫所有資料"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Booking")
        data = cursor.fetchall()
        conn.close()
        return data
    except sqlite3.Error as error:
        print(f"執行 SELECT 操作時發生錯誤：{error}")


def DBnew(name: str, day: str, phone: str, hct: int) -> bool:
    """使用者在資料庫中新增資料"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
                INSERT INTO Booking (Name, Day, Phone, Headcount)
                SELECT ?, ?, ?, ? WHERE NOT EXISTS (
                    SELECT 1 FROM Booking WHERE Phone=?);
            """, (name, day, phone, hct, phone),
        )
        print(f"=>異動 {cursor.rowcount} 筆記錄")
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as error:
        print(f"執行 SELECT 操作時發生錯誤：{error}")
        return False


def DBedit(mname: str, Day: str, uphone: str, hct: int) -> list:
    """修改資料庫指定資料"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Booking SET Day=?, mname=?, headcount=? WHERE mphone=?;",
            (Day, mname, hct, uphone),
        )
        print(f"=>異動 {cursor.rowcount} 筆記錄")
        conn.commit()
        conn.close()
        return DBsearch(uphone)
    except sqlite3.Error as error:
        print(f"執行 SELECT 操作時發生錯誤：{error}")


def DBsearch(uphone: str) -> list:
    """查詢資料庫指定資料，以電話搜尋"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Booking WHERE mphone=? ", (uphone,))
        DBdata = cursor.fetchall()  # 抓取所有資料
        if len(DBdata) > 0:  # 判斷有無資料
            for record in DBdata:
                return (record[1], record[2], record[3], record[4])
        conn.close()
    except sqlite3.Error as error:
        print(f"執行 SELECT 操作時發生錯誤：{error}")


def DBTableDelete() -> None:  # 完成
    """刪除資料表所有資料"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM  Booking")
        print(f"=>異動 {cursor.rowcount} 筆記錄")
        conn.commit()
        conn.close()
    except sqlite3.Error as error:
        print(f"執行 DELETE 操作時發生錯誤：{error}")


def DeleteData(uphone: str):  # 取消訂位
    try:
        conn = sqlite3.connect("booking.db")
        conn.execute("delete from Booking where Phone=?", (uphone,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"=>資料庫連接或資料表建立失敗，錯誤訊息為{e}")
