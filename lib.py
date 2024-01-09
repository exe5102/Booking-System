import configparser
import json
import re
import smtplib
import sqlite3
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

DB_PATH = "booking.db"
Pass_Data = "pass.json"
Room = {"單人房": 20, "雙人房": 20, "四人房": 20}
config_path = "config.ini"  # 配置文件(.ini)路徑


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
    minday = dt2 + timedelta(days=7)  # 在當前日期基礎上加7天
    timestr = minday.strftime("%Y-%m-%d")
    nowtm = dt2.strftime("%Y-%m-%d")

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
    Phone 文字 不可為空
    Roomtype 整數 不可為空
    Email 文字

    """
    try:
        conn = sqlite3.connect(DB_PATH)  # 連接資料庫
        cursor = conn.cursor()  # 建立cursor物件
        cursor.execute(
            """create table if not exists Booking(
                iid INTEGER PRIMARY KEY autoincrement,
                Name TEXT NOT NULL,
                DayStart TEXT NOT NULL,
                DayEnd TEXT NOT NULL,
                Phone TEXT NOT NULL,
                Roomtype INTEGER NOT NULL,
                Email TEXT
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


def DBnew(
    name: str, day_start: str, day_end: str, phone: str, rt: int, mail: str
) -> bool:
    """使用者在資料庫中新增資料"""

    # 將str日期轉成datetime物件
    datetime_start = datetime.strptime(day_start, "%Y-%m-%d")
    datetime_end = datetime.strptime(day_end, "%Y-%m-%d")

    # 若結束日比開始日早，代表輸入錯誤，不允許寫入ＤＢ
    if datetime_start > datetime_end:
        return False

    try:
        conn = sqlite3.connect(DB_PATH)  # 連接資料庫
        cursor = conn.cursor()  # 建立cursor物件
        #  不做重複檢查，一個人可定多房
        cursor.execute(
            """
                INSERT INTO Booking
                (Name, DayStart, DayEnd, Phone, Roomtype, Email)
                VALUES (?, ?, ?, ?, ?, ?);
            """,
            (name, day_start, day_end, phone, rt, mail),
        )
        print(f"=>異動 {cursor.rowcount} 筆記錄")
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as error:
        print(f"執行 SELECT 操作時發生錯誤：{error}")

    return False


def DBedit(iid: str, mname: str, day_start: str, day_end: str,
           uphone: str, rt: int) -> tuple:
    """修改資料庫指定資料"""
    try:
        conn = sqlite3.connect(DB_PATH)  # 連接資料庫
        cursor = conn.cursor()  # 建立cursor物件
        cursor.execute(
            "UPDATE Booking SET DayStart=?, DayEnd=?, Name=?, Roomtype=?,\
                Phone=? WHERE iid=?;",
            (day_start, day_end, mname, rt, uphone, iid),
        )
        print(f"=>異動 {cursor.rowcount} 筆記錄")
        conn.commit()
        conn.close()
        return DBsearch("id", iid)
    except sqlite3.Error as error:
        print(f"執行 SELECT 操作時發生錯誤：{error}")


def DBsearch(mode: str, data: str) -> list:
    """查詢資料庫指定資料，以電話搜尋"""
    try:
        conn = sqlite3.connect(DB_PATH)  # 連接資料庫
        cursor = conn.cursor()  # 建立cursor物件
        if mode == "id":
            cursor.execute("SELECT * FROM Booking WHERE iid=?", (data,))
        elif mode == "phone":
            cursor.execute("SELECT * FROM Booking WHERE Phone=?", (data,))
        DBdata = cursor.fetchall()  # 抓取所有資料
        if len(DBdata) > 0:  # 判斷有無資料
            return DBdata
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


def DeleteData(id: int) -> bool:
    """刪除資料庫中的指定資料"""
    try:
        conn = sqlite3.connect(DB_PATH)  # 連接資料庫
        cursor = conn.cursor()  # 建立cursor物件
        cursor.execute("delete from Booking where iid=?", (id,))
        print(f"=>異動 {cursor.rowcount} 筆記錄")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"=>資料庫連接或資料表建立失敗，錯誤訊息為{e}")
        return False


def roomlimit(roomtype: str) -> bool:  # 用途?
    """空房計算"""
    Room[roomtype] -= 1
    return False if Room[roomtype] < 0 else True


def roomstate():  # 用途?
    """空房資訊的讀取以及字典的初始化"""
    Room["單人房"] = 20
    Room["雙人房"] = 20
    Room["四人房"] = 20
    for record in DBAll():
        Room[record[5]] -= 1


def formatcheck(phone: str, email: str) -> bool:
    """電子郵件和電話的格式確認"""
    mailformat = r"[a-zA-Z0-9_.+-]+@[a-zA-Z]+[.a-zA-Z]+"
    phonformat = r"09\d{8}"

    # 若email不為空
    if email:
        # 全都檢查
        return (
            True
            if re.search(phonformat, phone) and re.search(mailformat, email)
            else False
        )
    else:
        # 不檢查email格式
        return True if re.search(phonformat, phone) else False


def send_booked_email(receiver_phone: str) -> bool:
    """寄送訂房成功通知信(mail)給客戶，以電話搜尋

    Args:
        receiver_phone (str): 客戶電話號碼

    Returns:
        bool: 推送是否成功
    """

    # 取得mail憑證
    sender_email, sender_password = getManagerCredentials(email=True)

    # 查找客戶資訊
    receiver_inf = DBsearch("phone", receiver_phone)
    receiver_name = receiver_inf[0][1]
    receiver_phone = receiver_inf[0][4]
    receiver_email = (
        receiver_inf[0][6]
        if receiver_inf[0][6] and formatcheck(receiver_phone,
                                              receiver_inf[0][6])
        else None
    )

    if receiver_email is None:
        print("通知郵件發送失敗，無有效的郵件地址")
        return False

    # 郵件正文
    html = f"""
            <h1>訂房成功！</h1>
            <br>
            <div>
                <h3>您的訂房資訊如下：</h3>
                <p>姓名：{receiver_name}</p>
                <p>電話：{receiver_phone}</p>
            """
    for item in receiver_inf:
        html += f"""
                    <br>
                    <p>房型：{item[5]}</p>
                    <p>訂房日期：{item[2]} ~ {item[3]}</p>
                """
    html += "</div>"

    # 創建多部分消息並設置標題
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "訂房成功通知"

    message.attach(MIMEText(html, "html", "UTF-8"))  # 寄送 HTML 格式的信件

    try:
        # 建立與SMTP服務器的連接並發送郵件
        server = smtplib.SMTP("smtp.gmail.com", 587)  # 使用Gmail的SMTP服務器
        server.ehlo()  # 建立連線並確認SMTP服務器狀態
        server.starttls()  # 啟用TLS安全
        server.login(sender_email, sender_password)  # 登入管理者mail
        # 寄送給客戶
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"發送通知郵件時出錯：{e}")
        return False


def send_booked_line(receiver_phone: str) -> bool:
    """推送客戶訂房資訊到管理者的line群組

    Args:
        receiver_phone (str): 客戶電話號碼

    Returns:
        bool: 推送是否成功
    """

    # 取得Line憑證
    url, token = getManagerCredentials(line=True)

    # 查找客戶資訊
    receiver_inf = DBsearch("phone", receiver_phone)
    receiver_name = receiver_inf[0][1]
    receiver_phone = receiver_inf[0][4]
    receiver_email = receiver_inf[0][6] if receiver_inf[0][6] else "X"

    headers = {"Authorization": "Bearer " + token}  # 設定token

    # 設定要發送的訊息
    context = (
        f"\n訂房成功！\n客戶姓名：{receiver_name}\n電話：{receiver_phone}"
        + f"\nemail：{receiver_email}\n"
    )
    for item in receiver_inf:  # 訊息中添加從同個人的多筆訂房取得的房型和時間
        context += f"\n房型：{item[5]}" + f"\n訂房日期：{item[2]} ~ {item[3]}\n"
    data = {"message": context}

    try:
        data = requests.post(url, headers=headers, data=data)  # 使用 POST 方法
        return True
    except Exception as e:
        print(e.__traceback__)
        return False


def getManagerCredentials(email: bool = False, line: bool = False) -> tuple:
    """取得管理者憑證，透過config.ini文件"""

    params = []

    # 讀取配置文件
    config = configparser.ConfigParser()
    config.read(config_path)

    # 取得EmailCredentials標籤下的資料
    sender_email = config.get("EmailCredentials", "sender_email")
    sender_password = config.get("EmailCredentials", "sender_password")

    # 取得LineCredentials標籤下的資料
    line_API = config.get("LineCredentials", "Line_Notify_API")
    line_token = config.get("LineCredentials", "Line_token")

    if email:
        params.append(sender_email)
        params.append(sender_password)
    if line:
        params.append(line_API)
        params.append(line_token)

    return tuple(params)
