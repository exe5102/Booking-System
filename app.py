from flask import (
    Flask,
    request,
    url_for,
    redirect,
    session,
    render_template)

from lib import (
    DBAll,
    DBcreate,
    DBnew,
    DBsearch,
    DeleteData,
    check,
    DateControl,
    DBedit)

DBcreate()

app = Flask(__name__)
app.config["SECRET_KEY"] = "Final-Projuct"
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/", methods=["GET", "POST"])  # 客戶訂房系統
def index():
    """
        當網頁Post進資料
        將資料包裝起來，進入BDnew()進行訂房，建立訂房資料
    """
    if request.method == "POST":
        uname = request.form["uname"]
        uphone = request.form["uphone"]
        Day = request.form["bookdate"]
        roomtype = request.form["roomtype"]
        if (uname == "" or uphone == "" or Day == "" or roomtype == ""):
            return redirect(url_for("failed"))
        else:
            if DBnew(uname, Day, uphone, roomtype):
                return redirect(url_for("Success"))
            else:
                return redirect(url_for("failed"))
    return render_template("index.html", min=DateControl()[0])


@app.route("/adminlogin", methods=["GET", "POST"])  # 管理端登入
def Adminlogin():
    """
        必須以session保存登入狀態，避免使用者誤入管理頁面
    """
    if request.method == "POST":
        act = request.form["account"]
        pw = request.form["password"]
        if check(act, pw) is True:
            session["loginAdminId"] = act
            return redirect(url_for("Administration"))
        return render_template("msg.html", msg="帳號密碼錯誤")
    return render_template("login.html")


@app.route("/failed")  # 客戶訂房失敗
def failed():
    """
        建立訂房資料失敗，導向訂房失敗頁面
    """
    return render_template("ResultFail.html")


@app.route("/success")  # 客戶訂房成功
def Success():
    """
        建立訂房資料成功，導向訂房成功頁面
    """
    return render_template("ResultSuccess.html")


@app.route("/search", methods=["GET", "POST"])  # 客戶查詢資料
def search():
    """
        客戶輸入資料，進入DBsearch()搜索資料庫，
        查無資料導向ResultSuccessFail.html網頁，
        有該筆資料導向search.html網頁並列印出資料。
    """
    if request.method == "POST":
        uphone = request.form["Sphone"]
        if DBsearch(uphone) is None:
            return render_template("ResultSuccessFail.html")
        else:
            return render_template("search.html", DBfatch=DBsearch(uphone))
    return render_template("search.html")

@app.route("/room")  # 客戶查詢資料
def room():
    return render_template("room.html")


@app.route("/adminhomepage")  # 管理端主頁
def Administration():
    if "loginAdminId" in session:
        return render_template("Admin.html", account=session["loginAdminId"])
    return render_template("msg.html", msg="請從主頁登入")


@app.route("/adminlogout")  # 管理端登出
def Adminlogout():
    """清空登入狀太，限制頁面載入"""
    session.pop("loginAdminId", None)
    return redirect(url_for("index"))


@app.route("/admindelete", methods=["GET", "POST"])  # 管理端取消訂單
def Admindelete():
    """
       管理端刪除訂房資料，先進DBsearch()搜索資料，再進行刪除，若無資料則導向ResultDeleteFail.html網頁
    """
    if "loginAdminId" in session:
        if request.method == "POST":
            uphone = request.form["Sphone"]
            data = DBsearch(uphone)
            if data is not None:
                DeleteData(uphone)
                return render_template("ResultDelete.html", DBfatch=data)
            else:
                return render_template("ResultDeleteFail.html")
        return render_template("AdminDelete.html")
    return render_template("msg.html", msg="請從主頁登入")


@app.route("/adminsearch", methods=["GET", "POST"])  # 管理端查詢指定客戶訂單
def Adminsearch():
    """
        管理端在登入狀態中，輸入資料進入DBsearch()搜索資料庫，
        查無資料導向ResultSuccessFailadmin.html網頁，
        有該筆資料導向AdminSearch.html網頁並列印出資料。
    """
    if "loginAdminId" in session:
        if request.method == "POST":
            uphone = request.form["Sphone"]
            if DBsearch(uphone) is None:
                return render_template("ResultSuccessFailadmin.html")
            else:
                return render_template("AdminSearch.html",
                                       DBfatch=DBsearch(uphone))
        return render_template("AdminSearch.html")
    return render_template("msg.html", msg="請從主頁登入")


@app.route("/adminalldata")  # 管理端列出所有資料
def AdminAlldata():
    """管理端呼叫資料庫中所有資料"""
    if "loginAdminId" in session:
        return render_template("AdminAllBooking.html", DBfatch=DBAll())
    return render_template("msg.html", msg="請從主頁登入")


@app.route("/adminedit")  # 管理端修改資料 網頁導向要更改
def AdminEdit():
    """管理端修改資料庫中的資料"""
    if "loginAdminId" in session:
        if request.method == "POST":
            uname = request.form["uname"]
            uphone = request.form["uphone"]
            Day = request.form["bookdate"]
            roomtype = request.form["roomtype"]
            if (uname == "" or uphone == "" or Day == "" or roomtype == ""):
                return redirect(url_for("failed"))
            else:
                if DBedit(uname, Day, uphone, roomtype):
                    return redirect(url_for("Success"))
                else:
                    return redirect(url_for("failed"))
        return render_template("AdminSearch copy.html")
    return render_template("msg.html", msg="請從主頁登入")


@app.route("/useredit")  # 客戶端修改資料 網頁導向要更改
def UserEdit():
    if request.method == "POST":
        uname = request.form["uname"]
        uphone = request.form["uphone"]
        Day = request.form["bookdate"]
        roomtype = request.form["roomtype"]
        if (uname == "" or uphone == "" or Day == "" or roomtype == ""):
            return redirect(url_for("failed"))
        else:
            if DBedit(uname, Day, uphone, roomtype):
                return redirect(url_for("Success"))
            else:
                return redirect(url_for("failed"))
    return render_template("AdminSearch copy.html")