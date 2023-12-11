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
    DateControl)

DBcreate()

app = Flask(__name__)
# app.config["ENV"] = "development"
# app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "Final-Projuct"
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/", methods=["GET", "POST"])  # 客戶訂位系統
def index():
    if request.method == "POST":
        uname = request.form["uname"]
        uphone = request.form["uphone"]
        Day = request.form["bookdate"]
        headcount = request.form["headcount"]
        if (uname == "" or uphone == "" or Day == "" or headcount == ""):
            print("1")
            return redirect(url_for("failed"))
        else:
            if DBnew(uname, uphone, Day, headcount):
                return redirect(url_for("Success"))
            else:
                print("2")
                return redirect(url_for("failed"))
    return render_template("index.html", min=DateControl()[0])


@app.route("/adminlogin", methods=["GET", "POST"])  # 管理端登入
def Adminlogin():
    if request.method == "POST":
        act = request.form["account"]
        pw = request.form["password"]
        if check(act, pw) is True:
            session["loginAdminId"] = act
            return redirect(url_for("Administration"))
        return render_template("msg.html", msg="帳號密碼錯誤")
    return render_template("login.html")


@app.route("/failed")  # 客戶訂位失敗
def failed():
    return render_template("ResultFail.html")


@app.route("/success")  # 客戶訂位成功
def Success():
    return render_template("ResultSuccess.html")


@app.route("/search", methods=["GET", "POST"])  # 客戶查詢訂單
def search():
    if request.method == "POST":
        uphone = request.form["Sphone"]
        return render_template("search.html", DBfatch=DBsearch(uphone))
    return render_template("search.html")


@app.route("/adminhomepage")  # 管理端主頁
def Administration():
    if "loginAdminId" in session:
        return render_template("Admin.html", account=session["loginAdminId"])
    return render_template("msg.html", msg="請從主頁登入")


@app.route("/adminlogout")  # 管理端登出
def Adminlogout():
    session.pop("loginAdminId", None)
    return redirect(url_for("index"))


@app.route("/admindelete", methods=["GET", "POST"])  # 管理端取消訂單
def Admindelete():
    if "loginAdminId" in session:
        if request.method == "POST":
            uphone = request.form["Sphone"]
            Data = DBsearch(uphone)
            DeleteData(uphone)
            return render_template("ResultDelete.html", DBfatch=Data)
        return render_template("AdminDelete.html")
    return render_template("msg.html", msg="請從主頁登入")


@app.route("/adminsearch", methods=["GET", "POST"])  # 管理端查詢指定客戶訂單
def Adminsearch():
    if "loginAdminId" in session:
        if request.method == "POST":
            uphone = request.form["Sphone"]
            return render_template("AdminSearch.html",
                                   DBfatch=DBsearch(uphone))
        return render_template("AdminSearch.html")
    return render_template("msg.html", msg="請從主頁登入")


@app.route("/adminalldata")  # 管理端列出所有資料
def AdminAlldata():
    if "loginAdminId" in session:
        return render_template("AdminAllBooking.html", DBfatch=DBAll())
    return render_template("msg.html", msg="請從主頁登入")
