import os
from datetime import date

import pandas as pd
from flask import Flask, render_template, request
from sqlalchemy import create_engine

server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
driver = "ODBC+Driver+18+for+SQL+Server"
connection_url = (
    f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"
)
engine = create_engine(connection_url)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    clues_df = pd.read_sql(
        """
        select top 100 clue, answer, count(*) as occurrences 
        from clues group by clue, answer 
        order by occurrences desc
    """,
        engine,
    )
    answers_df = pd.read_sql(
        """
        select top 100 answer, count (*) as occurrences
        from clues group by answer
        order by occurrences desc
    """,
        engine,
    )
    return render_template(
        "home.html",
        table1=clues_df.to_html(classes="styled-table", index=False),
        table2=answers_df.to_html(classes="styled-table", index=False),
    )


@app.route("/day", methods=["POST"])
def day():
    selected_date = request.form.get("date")
    clues_df = pd.read_sql(
        f"""
        select top 100 c.clue, c.answer, c.occurrences from clues join 
        (select clue, answer, count(*) as occurrences from clues group by clue, answer) as c 
        on clues.clue = c.clue and clues.answer = c.answer
        where date = '{selected_date}' and c.occurrences > 1 order by c.occurrences desc;
    """,
        engine,
    )
    answers_df = pd.read_sql(
        f"""
        select top 100 c.answer, c.occurrences from clues join 
        (select answer, count(*) as occurrences from clues group by answer) as c 
        on clues.answer = c.answer
        where date = '{selected_date}' and c.occurrences > 1 order by c.occurrences desc;
    """,
        engine,
    )
    return render_template(
        "day.html",
        selected_date=selected_date,
        table1=clues_df.to_html(classes="styled-table", index=False),
        table2=answers_df.to_html(classes="styled-table", index=False),
    )


@app.route("/clue", methods=["POST"])
def clue():
    search_clue = request.form.get("search_clue")
    search_clue = search_clue.replace("'", "''")
    df = pd.read_sql(
        f"""
        select clue, answer, count(*) as occurrences
        from clues
        where clue LIKE '%{search_clue}%' 
        group by clue, answer order by count(*) desc;
    """,  # or #CONTAINS(clue, '{search_clue}')
        engine,
    )
    return render_template(
        "clue.html", table=df.to_html(classes="styled-table", index=False)
    )


@app.route("/answer", methods=["POST"])
def answer():
    search_answer = request.form.get("search_answer")
    search_answer = search_answer.replace("'", "''")
    df = pd.read_sql(
        f"""
        select clue, answer, count(*) as occurrences
        from clues
        where answer LIKE '{search_answer}'
        group by clue, answer order by count(*) desc;
    """,
        engine,
    )
    return render_template(
        "answer.html", table=df.to_html(classes="styled-table", index=False)
    )


if __name__ == "__main__":
    app.run(debug=True)
