from Stock import Stock
from User import User
from Forms import Login_form,Register_form
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from bcrypt import checkpw, hashpw, gensalt
import os



def create_app():
  app=Flask(__name__)
  app.secret_key = 'the random string'
  login_manager = LoginManager()
  login_manager.init_app(app)
  login_manager.login_view = "login"
  login_manager.login_message = "Aby uzyskać dostęp do tej strony musisz się zalogować "
  login_manager.login_message_category = "danger"
  stock_list = Stock.stock_list()

  @login_manager.user_loader
  def load_user(user_name):
    return User(user_name)

  @app.route("/", methods=["POST","GET"])
  def index():
    user = current_user
    if user.is_active:
      balance = float(user.get_balance())
      balance= f"Dostępne saldo: {balance:.2f} zł."
    else:
      balance= ""
    return render_template("index.html",balance=balance,
                           stock=zip(stock_list, stock_list.values(),
                                     range(1, len(stock_list)+1)))
  @app.route("/stats", methods=["POST","GET"])
  @login_required
  def stats():
    user = current_user
    balance = float(user.get_balance())
    share_value = (user.get_share_value())
    altogether = balance+share_value
    share_value = f"{share_value:.2f}"
    altogether = f"{altogether:.2f}"
    balance = f"{balance:.2f}"
    return render_template("stats.html",altogether=altogether,share_value=share_value,balance=balance,stock=stock_list,owned_shares=zip(user.get_stats(),user.get_stats().values(),range(1,1+len(user.get_stats()))))

  @app.route("/ranking", methods=["POST","GET"])
  def ranking():
    users_collection=User.users_collection()
    ranking=users_collection.find({}).sort("balance",-1)
    return render_template("ranking.html",ranking=zip(ranking,range(1,1+ranking.count())))

  @app.route("/login", methods=["POST","GET"])
  def login():
    form = Login_form()
    if form.validate_on_submit():
      user = User(form.user_name.data)
      users_collection = user.users_collection()
      cursor=users_collection.find_one({"user_name": form.user_name.data})
      if cursor and checkpw(form.password.data.encode('utf-8'), cursor["password"]):
        login_user(user)
        flash("Zalogownano pomyślnie", category="success")
        return redirect(request.args.get("next") or url_for("index"))
      else:
        flash("Wprowadzone dane są nieprawidłowe", category="danger")
    return render_template("login.html", form=form)

  @app.route("/register", methods=["POST", "GET"])
  def register():
    form = Register_form()
    if form.validate_on_submit():
      users_collection = User.users_collection()
      users_collection.insert_one({"user_name": form.user_name.data,
                                   "password":hashpw(form.password.data.encode("utf-8"), gensalt()),
                                   "balance": 1000, "e-mail": form.email.data})
      flash("Rejerstracja przebiegła pomyślnie teraz możesz się zalogować", category="success")
      return redirect(url_for("index"))
    return render_template("register.html", form=form)

  @app.route("/buy/<company_name>", methods=["POST", "GET"])
  @login_required
  def buy(company_name):
    user=current_user
    verification=user.buy(company_name,((request.form.get("quantity"))))
    if not verification:
      flash("Twój stan konta nie pozwala na dokonanie tej operacji",category="danger")
    return redirect(url_for("index"))

  @app.route("/sell/<company_name>",methods=["POST","GET"])
  def sell(company_name):
    user = current_user
    verification = user.sell(company_name, (request.form.get("quantity")))
    if not verification:
      flash("Masz za mało akcji aby dokonać tej tranzakcji", category="danger")
    return redirect(url_for("stats"))

  @app.route("/logout", methods=["POST", "GET"])
  def logout():
    logout_user()
    return redirect(url_for("index"))
  return app


create_app().run()
















