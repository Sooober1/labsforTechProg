"""
Лабораторная работа 2. Уязвимое веб-приложение.
Простой сайт-«гостевая книга» с входом в аккаунт.

ВНИМАНИЕ: здесь СПЕЦИАЛЬНО сделаны 2 уязвимости (OWASP Top 10):
  1) SQL-инъекция  (OWASP A03: Injection)
  2) XSS           (OWASP A03: Injection / Cross-Site Scripting)

Приложение учебное, запускать только локально.
"""

import sqlite3
from flask import Flask, request, redirect, make_response
from html import escape  # для защиты от XSS

app = Flask(__name__)
DB = "app.db"


def init_db():
    """Создаём базу и кладём туда одного пользователя и пару сообщений."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("DROP TABLE IF EXISTS messages")
    c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    c.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, text TEXT)")
    # секретный пароль админа — его мы и будем "обходить"
    c.execute("INSERT INTO users (username, password) VALUES ('admin', 'SuperSecret123')")
    c.execute("INSERT INTO messages (text) VALUES ('Привет! Это гостевая книга.')")
    conn.commit()
    conn.close()


@app.route("/")
def index():
    """Главная страница: форма входа + гостевая книга."""
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT text FROM messages").fetchall()
    conn.close()

    # ИСПРАВЛЕНО (XSS): экранируем текст перед вставкой в HTML.
    # escape() превращает <script> в безопасный &lt;script&gt;,
    # и браузер показывает его как текст, а не выполняет.
    messages_html = ""
    for r in rows:
        messages_html += "<p>" + escape(r[0]) + "</p>"

    return """
    <h1>Гостевая книга</h1>
    <h3>Вход</h3>
    <form action="/login" method="post">
      Логин: <input name="username"><br>
      Пароль: <input name="password" type="password"><br>
      <button>Войти</button>
    </form>
    <h3>Сообщения</h3>
    """ + messages_html + """
    <h3>Оставить сообщение</h3>
    <form action="/add" method="post">
      <input name="text">
      <button>Отправить</button>
    </form>
    """


@app.route("/login", methods=["POST"])
def login():
    """Проверка логина и пароля."""
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    # ИСПРАВЛЕНО (SQL-инъекция): используем параметры (знаки ?).
    # Теперь логин и пароль передаются отдельно от текста запроса,
    # и их нельзя "подмешать" в сам SQL.
    query = "SELECT * FROM users WHERE username=? AND password=?"

    conn = sqlite3.connect(DB)
    user = conn.execute(query, (username, password)).fetchone()
    conn.close()

    if user:
        return "<h2>Добро пожаловать, " + username + "! Вход выполнен.</h2>"
    return "<h2>Неверный логин или пароль</h2>"


@app.route("/add", methods=["POST"])
def add():
    """Добавить сообщение в гостевую книгу."""
    text = request.form.get("text", "")
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO messages (text) VALUES (?)", (text,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
