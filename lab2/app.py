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
    """Главная страница демо-стенда."""
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT text FROM messages").fetchall()
    conn.close()

    # ===== УЯЗВИМОСТЬ 2: XSS =====
    # Текст сообщений вставляется в HTML как есть, без экранирования.
    # Если кто-то отправит <script>...</script>, он выполнится у всех.
    messages_html = ""
    for r in rows:
        messages_html += "<p>" + r[0] + "</p>"

    return """
    <meta charset="utf-8">
    <h1>Тест</h1>

    <h3>Вход</h3>
    <p>Тут можно попробовать SQL-инъекцию.</p>
    <form action="/login" method="post">
      Логин: <input name="username"><br>
      Пароль: <input name="password"><br>
      <button>Войти</button>
    </form>

    <h3>Сообщения</h3>
    <p>Сюда попадает всё, что отправили ниже. Тут можно попробовать XSS: если
    отправить скрипт вместо текста, он выполнится.</p>
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

    # ===== УЯЗВИМОСТЬ 1: SQL-инъекция =====
    # Логин и пароль напрямую склеиваются в SQL-запрос.
    # Можно подставить ' OR '1'='1 и войти без пароля.
    query = "SELECT * FROM users WHERE username='" + username + \
            "' AND password='" + password + "'"

    conn = sqlite3.connect(DB)
    user = conn.execute(query).fetchone()
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
