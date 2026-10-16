from flask import Flask, request, redirect, render_template_string, url_for
import sqlite3
import secrets
from urllib.parse import urlparse

app = Flask(__name__)
DATABASE = "urls.db"


# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# CREATE DATABASE TABLE
def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT UNIQUE NOT NULL,
                clicks INTEGER DEFAULT 0
            )
        """)


# VALIDATE URL
def is_valid_url(value):
    try:
        parsed = urlparse(value)
        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.hostname)
            and not any(c.isspace() for c in value)
        )
    except ValueError:
        return False


# HTML + CSS
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>LinkLite | URL Shortener</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            background: #0b1020;
            color: #f3f4f6;
            font-family: Arial, sans-serif;
            display: grid;
            place-items: center;
            padding: 24px;
        }

        main {
            width: 100%;
            max-width: 720px;
        }

        .brand {
            color: #a99bff;
            font-weight: bold;
            letter-spacing: 2px;
        }

        h1 {
            font-size: clamp(32px, 6vw, 52px);
            margin-bottom: 12px;
        }

        .muted {
            color: #9ca3af;
            line-height: 1.7;
        }

        .panel {
            background: #141b2e;
            border: 1px solid #29334b;
            padding: 24px;
            border-radius: 18px;
            margin-top: 24px;
        }

        input {
            width: 100%;
            padding: 15px;
            margin: 12px 0;
            border-radius: 10px;
            border: 1px solid #374151;
            background: #0b1020;
            color: white;
            font-size: 15px;
        }

        button {
            padding: 14px 20px;
            background: #8875ff;
            color: white;
            border: 0;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.2s ease;
        }

        button:hover {
            background: #7059f0;
        }

        .result {
            padding: 16px;
            margin-top: 18px;
            background: #202a42;
            border-radius: 12px;
            overflow-wrap: anywhere;
        }

        a {
            color: #b8adff;
            overflow-wrap: anywhere;
        }

        .stats {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            margin-top: 22px;
        }

        .stat {
            flex: 1;
            min-width: 130px;
            background: #141b2e;
            border: 1px solid #29334b;
            padding: 18px;
            border-radius: 14px;
        }

        .number {
            font-size: 28px;
            font-weight: bold;
            margin-top: 8px;
        }

        .error {
            color: #fca5a5;
        }

        .saved {
            border-bottom: 1px solid #29334b;
            padding: 14px 0;
        }

        .saved:last-child {
            border-bottom: 0;
        }

        .small {
            font-size: 13px;
            overflow-wrap: anywhere;
        }

        /* NOOR SHAIKH FOOTER */

        .footer {
            width: 100%;
            text-align: center;
            margin-top: 35px;
            padding: 22px 10px;
            color: #b8adff;
            font-size: 13px;
            letter-spacing: 0.7px;
            border-top: 1px solid #29334b;
            line-height: 1.8;
        }

        .footer span {
            color: #ffffff;
            font-weight: bold;
        }

        @media (max-width: 480px) {
            body {
                padding: 16px;
            }

            .panel {
                padding: 18px;
            }

            button {
                max-width: 100%;
            }
        }
    </style>
</head>

<body>

<main>

    <div class="brand">LINKLITE / PYTHON PROJECT</div>

    <h1>Short links.<br>Simple analytics.</h1>

    <p class="muted">
        Turn long URLs into short, shareable links.
        Track clicks and manage your saved links.
    </p>

    <section class="panel">

        <h2>Create a short link</h2>

        <form method="POST" action="/">

            <label for="original_url">
                Paste your original URL
            </label>

            <input
                id="original_url"
                name="original_url"
                type="url"
                placeholder="https://example.com/your-long-link"
                required
            >

            <button type="submit">
                Shorten URL ↗
            </button>

        </form>

        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}

        {% if created %}
            <div class="result">

                <p>Your short link is ready!</p>

                <a
                    id="shortLink"
                    href="{{ created }}"
                >{{ created }}</a>

                <button
                    type="button"
                    onclick="copyLink()"
                >
                    Copy link
                </button>

            </div>
        {% endif %}

    </section>

    <div class="stats">

        <div class="stat">
            <div class="muted">Total links</div>
            <div class="number">{{ total_links }}</div>
        </div>

        <div class="stat">
            <div class="muted">Total clicks</div>
            <div class="number">{{ total_clicks }}</div>
        </div>

    </div>

    <section class="panel">

        <h2>Saved links</h2>

        {% for item in links %}

            <div class="saved">

                <a href="{{ url_for('open_short', code=item['short_code']) }}">
                    {{ request.host_url }}{{ item['short_code'] }}
                </a>

                <p class="muted small">
                    {{ item['original_url'] }}
                </p>

                <p class="muted">
                    {{ item['clicks'] }} clicks
                </p>

            </div>

        {% else %}

            <p class="muted">
                No links yet. Create your first short link!
            </p>

        {% endfor %}

    </section>

    <!-- WEBSITE CREDIT -->

    <footer class="footer">
        Engineered to Perfection by
        <span>Noor Shaikh</span>
    </footer>

</main>

<script>
function copyLink() {
    const link = document.getElementById("shortLink").href;

    navigator.clipboard.writeText(link)
        .then(() => alert("Short link copied!"))
        .catch(() => prompt("Copy your link:", link));
}
</script>

</body>
</html>
"""


# HOME PAGE
@app.route("/", methods=["GET", "POST"])
def home():

    created = None
    error = None

    if request.method == "POST":

        original_url = request.form.get(
            "original_url", ""
        ).strip()

        if not is_valid_url(original_url):

            error = "Please enter a valid HTTP or HTTPS URL."

        else:

            with get_db() as conn:

                while True:

                    code = secrets.token_urlsafe(5)

                    try:
                        conn.execute(
                            """
                            INSERT INTO urls
                            (original_url, short_code)
                            VALUES (?, ?)
                            """,
                            (original_url, code),
                        )
                        break

                    except sqlite3.IntegrityError:
                        continue

            created = url_for(
                "open_short",
                code=code,
                _external=True
            )

    with get_db() as conn:

        links = conn.execute(
            "SELECT * FROM urls ORDER BY id DESC"
        ).fetchall()

        total_links = conn.execute(
            "SELECT COUNT(*) FROM urls"
        ).fetchone()[0]

        total_clicks = conn.execute(
            "SELECT COALESCE(SUM(clicks), 0) FROM urls"
        ).fetchone()[0]

    return render_template_string(
        HTML,
        created=created,
        error=error,
        links=links,
        total_links=total_links,
        total_clicks=total_clicks,
    )


# SHORT LINK REDIRECT
@app.route("/<code>")
def open_short(code):

    with get_db() as conn:

        item = conn.execute(
            "SELECT original_url FROM urls WHERE short_code = ?",
            (code,),
        ).fetchone()

        if item is None:
            return "Short link not found.", 404

        conn.execute(
            "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?",
            (code,),
        )

        original_url = item["original_url"]

    return redirect(original_url, code=302)


# INITIALIZE DATABASE
init_db()


# RUN WEBSITE
if __name__ == "__main__":
    app.run(debug=True)




# from flask import Flask, request, redirect, render_template_string, url_for
# import sqlite3
# import secrets
# from urllib.parse import urlparse

# app = Flask(__name__)
# DATABASE = "urls.db"


# def get_db():
#     conn = sqlite3.connect(DATABASE)
#     conn.row_factory = sqlite3.Row
#     return conn


# def init_db():
#     with get_db() as conn:
#         conn.execute("""
#             CREATE TABLE IF NOT EXISTS urls (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 original_url TEXT NOT NULL,
#                 short_code TEXT UNIQUE NOT NULL,
#                 clicks INTEGER DEFAULT 0
#             )
#         """)


# def is_valid_url(value):
#     try:
#         parsed = urlparse(value)
#         return (
#             parsed.scheme in ("http", "https")
#             and bool(parsed.hostname)
#             and not any(c.isspace() for c in value)
#         )
#     except ValueError:
#         return False


# HTML = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1">
#     <title>LinkLite | URL Shortener</title>
#     <style>
#         * { box-sizing: border-box; }
#         body {
#             margin: 0;
#             min-height: 100vh;
#             background: #0b1020;
#             color: #f3f4f6;
#             font-family: Arial, sans-serif;
#             display: grid;
#             place-items: center;
#             padding: 24px;
#         }
#         main { width: 100%; max-width: 720px; }
#         .brand { color: #a99bff; font-weight: bold; letter-spacing: 2px; }
#         h1 { font-size: clamp(32px, 6vw, 52px); margin-bottom: 12px; }
#         .muted { color: #9ca3af; line-height: 1.7; }
#         .panel {
#             background: #141b2e;
#             border: 1px solid #29334b;
#             padding: 24px;
#             border-radius: 18px;
#             margin-top: 24px;
#         }
#         input {
#             width: 100%;
#             padding: 15px;
#             margin: 12px 0;
#             border-radius: 10px;
#             border: 1px solid #374151;
#             background: #0b1020;
#             color: white;
#             font-size: 15px;
#         }
#         button {
#             padding: 14px 20px;
#             background: #8875ff;
#             color: white;
#             border: 0;
#             border-radius: 10px;
#             cursor: pointer;
#             font-weight: bold;
#         }
#         button:hover { background: #7059f0; }
#         .result {
#             padding: 16px;
#             margin-top: 18px;
#             background: #202a42;
#             border-radius: 12px;
#             overflow-wrap: anywhere;
#         }
#         a { color: #b8adff; }
#         .stats {
#             display: flex;
#             gap: 16px;
#             flex-wrap: wrap;
#             margin-top: 22px;
#         }
#         .stat {
#             flex: 1;
#             min-width: 130px;
#             background: #141b2e;
#             border: 1px solid #29334b;
#             padding: 18px;
#             border-radius: 14px;
#         }
#         .number { font-size: 28px; font-weight: bold; margin-top: 8px; }
#         .error { color: #fca5a5; }
#         .saved { border-bottom: 1px solid #29334b; padding: 14px 0; }
#         .saved:last-child { border-bottom: 0; }
#         .small { font-size: 13px; overflow-wrap: anywhere; }
#     </style>
# </head>
# <body>
# <main>
#     <div class="brand">LINKLITE / PYTHON PROJECT</div>
#     <h1>Short links.<br>Simple analytics.</h1>
#     <p class="muted">
#         Turn long URLs into short, shareable links.
#         Track clicks and manage your saved links.
#     </p>

#     <section class="panel">
#         <h2>Create a short link</h2>
#         <form method="POST" action="/">
#             <label for="original_url">Paste your original URL</label>
#             <input
#                 id="original_url"
#                 name="original_url"
#                 type="url"
#                 placeholder="https://example.com/your-long-link"
#                 required
#             >
#             <button type="submit">Shorten URL ↗</button>
#         </form>

#         {% if error %}
#             <p class="error">{{ error }}</p>
#         {% endif %}

#         {% if created %}
#             <div class="result">
#                 <p>Your short link is ready!</p>
#                 <a id="shortLink" href="{{ created }}">{{ created }}</a>
#                 <button type="button" onclick="copyLink()">Copy link</button>
#             </div>
#         {% endif %}
#     </section>

#     <div class="stats">
#         <div class="stat">
#             <div class="muted">Total links</div>
#             <div class="number">{{ total_links }}</div>
#         </div>
#         <div class="stat">
#             <div class="muted">Total clicks</div>
#             <div class="number">{{ total_clicks }}</div>
#         </div>
#     </div>

#     <section class="panel">
#         <h2>Saved links</h2>
#         {% for item in links %}
#             <div class="saved">
#                 <a href="{{ url_for('open_short', code=item['short_code']) }}">
#                     {{ request.host_url }}{{ item['short_code'] }}
#                 </a>
#                 <p class="muted small">{{ item['original_url'] }}</p>
#                 <p class="muted">{{ item['clicks'] }} clicks</p>
#             </div>
#         {% else %}
#             <p class="muted">No links yet. Create your first short link!</p>
#         {% endfor %}
#     </section>
# </main>

# <script>
# function copyLink() {
#     const link = document.getElementById("shortLink").href;
#     navigator.clipboard.writeText(link)
#         .then(() => alert("Short link copied!"))
#         .catch(() => prompt("Copy your link:", link));
# }
# </script>
# </body>
# </html>
# """


# @app.route("/", methods=["GET", "POST"])
# def home():
#     created = None
#     error = None

#     if request.method == "POST":
#         original_url = request.form.get("original_url", "").strip()

#         if not is_valid_url(original_url):
#             error = "Please enter a valid HTTP or HTTPS URL."
#         else:
#             with get_db() as conn:
#                 while True:
#                     code = secrets.token_urlsafe(5)
#                     try:
#                         conn.execute(
#                             """INSERT INTO urls
#                                (original_url, short_code)
#                                VALUES (?, ?)""",
#                             (original_url, code),
#                         )
#                         break
#                     except sqlite3.IntegrityError:
#                         continue

#             created = url_for(
#                 "open_short", code=code, _external=True
#             )

#     with get_db() as conn:
#         links = conn.execute(
#             "SELECT * FROM urls ORDER BY id DESC"
#         ).fetchall()

#         total_links = conn.execute(
#             "SELECT COUNT(*) FROM urls"
#         ).fetchone()[0]

#         total_clicks = conn.execute(
#             "SELECT COALESCE(SUM(clicks), 0) FROM urls"
#         ).fetchone()[0]

#     return render_template_string(
#         HTML,
#         created=created,
#         error=error,
#         links=links,
#         total_links=total_links,
#         total_clicks=total_clicks,
#     )


# @app.route("/<code>")
# def open_short(code):
#     with get_db() as conn:
#         item = conn.execute(
#             "SELECT original_url FROM urls WHERE short_code = ?",
#             (code,),
#         ).fetchone()

#         if item is None:
#             return "Short link not found.", 404

#         conn.execute(
#             "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?",
#             (code,),
#         )
#         original_url = item["original_url"]

#     return redirect(original_url, code=302)


# init_db()

# if __name__ == "__main__":
#     app.run(debug=True)
# # 