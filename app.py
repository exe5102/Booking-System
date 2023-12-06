from Clientlib import (
    ClientBK,
    ClientSearch,
)
from Adminlib import (
    AdminCheck,
    AdminDelete,
    Search,
    BuildDB,
    DateControl,
    SearchAll,
)
from flask import (
    Flask,
    request,
    url_for,
    redirect,
    session,
    render_template)

BuildDB()

app = Flask(__name__)
# app.config["ENV"] = "development"
# app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "Final-Projuct"
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/", methods=["GET", "POST"])  # 客戶訂位系統
def index():
    if request.method == "POST":
        uid = request.form["uid"]
        uphone = request.form["uphone"]
        sday = request.form["bookdate"]
        unumber = request.form["unumber"]
        stime = request.form["time"]
        if (
            uid == ""
            or uphone == ""
            or sday == ""
            or unumber == "請選擇人數"
            or stime == "請選擇時段"
        ):
            return redirect(url_for("failed"))
        # print(uid)
        else:
            ClientBK(uid, uphone, unumber, sday, stime)
            return redirect(url_for("Success"))

    return render_template(
        "index.html", today=DateControl()[0], min=DateControl()[1]
    )


@app.route("/adminlogin", methods=["GET", "POST"])  # 管理端登入
def Adminlogin():
    if request.method == "POST":
        account = request.form["account"]
        password = request.form["password"]
        if AdminCheck(account, password) is True:
            session["loginAdminId"] = account
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
        Sphone = request.form["Sphone"]
        return render_template("search.html", DBfatch=ClientSearch(Sphone))
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
            Data = ClientSearch(uphone)
            AdminDelete(uphone)
            return render_template("ResultDelete.html", DBfatch=Data)
        return render_template("AdminDelete.html")
    return render_template("msg.html", msg="請從主頁登入")


@app.route("/adminsearch", methods=["GET", "POST"])  # 管理端查詢指定客戶訂單
def Adminsearch():
    if "loginAdminId" in session:
        if request.method == "POST":
            Sphone = request.form["Sphone"]
            return render_template("AdminSearch.html",
                                   DBfatch=Search(Sphone))
        return render_template("AdminSearch.html")
    return render_template("msg.html", msg="請從主頁登入")


@app.route("/adminalldata")  # 管理端列出所有資料
def AdminAlldata():
    if "loginAdminId" in session:
        return render_template("AdminAllBooking.html", DBfatch=SearchAll())
    return render_template("msg.html", msg="請從主頁登入")
