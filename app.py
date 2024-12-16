import os
from datetime import date

import pandas as pd
from dotenv import load_dotenv
from flask import Flask, render_template, request
from sqlalchemy import create_engine

load_dotenv()

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
        select top 100 Clue, Answer, count(*) as Count 
        from clues group by clue, answer 
        order by count desc
    """,
        engine,
    )
    answers_df = pd.read_sql(
        """
        select top 100 Answer, count (*) as Count
        from clues group by answer
        order by count desc
    """,
        engine,
    )
    return render_template(
        "home.html",
        table1=clues_df.to_html(classes="styled-table", index=False),
        table2=answers_df.to_html(classes="styled-table", index=False),
    )


@app.route("/day", methods=["GET"])
def day():
    selected_date = request.args.get("date")
    clues_df = pd.read_sql(
        f"""
        select top 100 c.Clue, c.Answer, c.Count from clues join 
        (select clue, answer, count(*) as count from clues group by clue, answer) as c 
        on clues.clue = c.clue and clues.answer = c.answer
        where date = '{selected_date}' and c.count > 1 order by c.count desc;
    """,
        engine,
    )
    answers_df = pd.read_sql(
        f"""
        select top 100 c.Answer, c.Count from clues join 
        (select answer, count(*) as count from clues group by answer) as c 
        on clues.answer = c.answer
        where date = '{selected_date}' and c.count > 1 order by c.count desc;
    """,
        engine,
    )
    return render_template(
        "day.html",
        selected_date=selected_date,
        table1=clues_df.to_html(classes="styled-table", index=False),
        table2=answers_df.to_html(classes="styled-table", index=False),
    )


@app.route("/clue", methods=["GET"])
def clue():
    search_clue = request.args.get("search_clue")
    search_clue = search_clue.replace("'", "''")
    df = pd.read_sql(
        f"""
        select top 100 Clue, Answer, count(*) as Count
        from clues
        where clue LIKE '%{search_clue}%' 
        group by clue, answer order by count(*) desc;
    """,  # or #CONTAINS(clue, '{search_clue}')
        engine,
    )
    return render_template(
        "clue.html",
        search_clue=search_clue,
        table=df.to_html(classes="styled-table", index=False),
    )


@app.route("/answer", methods=["GET"])
def answer():
    search_answer = request.args.get("search_answer")
    search_answer = search_answer.replace("'", "''")
    df = pd.read_sql(
        f"""
        select top 100 Clue, Answer, count(*) as Count
        from clues
        where answer LIKE '{search_answer}'
        group by clue, answer order by count(*) desc;
    """,
        engine,
    )
    return render_template(
        "answer.html",
        search_answer=search_answer,
        table=df.to_html(classes="styled-table", index=False),
    )


if __name__ == "__main__":
    app.run(debug=True)
