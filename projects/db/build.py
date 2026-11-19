# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo",
# ]
# ///
"""Database Project, Part A: build the BabsonAI Labs database."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import duckdb
    import polars as pl

    return duckdb, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part A: Design and Build

    The design is in `README.md` next to this notebook. This notebook creates
    `database.duckdb` from nothing on every run, from the CSVs in `data/`,
    which `make_data.py` wrote.
    """)
    return


@app.cell
def _(duckdb, mo):
    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return ask, database


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Tables

    One `CREATE TABLE` per ERD table, every primary and foreign key declared,
    with `NOT NULL`, `UNIQUE`, and `CHECK` where the lab's rules call for them.
    The build cell below deletes the old file, creates the tables, loads the
    data, and saves the view, all inside one connection that closes at the end.
    """)
    return


@app.cell
def _(database, duckdb, mo):
    create_statements = [
        """
        CREATE TABLE people (
            person_id INTEGER PRIMARY KEY,
            first_name VARCHAR NOT NULL,
            last_name VARCHAR NOT NULL,
            work_email VARCHAR NOT NULL UNIQUE,
            title VARCHAR NOT NULL,
            start_date DATE NOT NULL,
            manager_id INTEGER REFERENCES people(person_id)
        )
        """,
        """
        CREATE TABLE projects (
            project_id INTEGER PRIMARY KEY,
            project_name VARCHAR NOT NULL UNIQUE,
            client VARCHAR,
            category VARCHAR NOT NULL
                CHECK (category IN ('LLM app', 'data pipeline', 'internal tool')),
            budget_dollars DECIMAL(12, 2) NOT NULL CHECK (budget_dollars > 0),
            start_date DATE NOT NULL,
            status VARCHAR NOT NULL
                CHECK (status IN ('planned', 'active', 'paused', 'done'))
        )
        """,
        """
        CREATE TABLE assignments (
            person_id INTEGER NOT NULL REFERENCES people(person_id),
            project_id INTEGER NOT NULL REFERENCES projects(project_id),
            role VARCHAR NOT NULL,
            hours_per_week INTEGER NOT NULL CHECK (hours_per_week BETWEEN 1 AND 40),
            joined_date DATE NOT NULL,
            PRIMARY KEY (person_id, project_id)
        )
        """,
        """
        CREATE TABLE tasks (
            task_id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL REFERENCES projects(project_id),
            description VARCHAR NOT NULL,
            created_date DATE NOT NULL,
            assignee_id INTEGER REFERENCES people(person_id),
            due_date DATE NOT NULL,
            completed_date DATE,
            CHECK (completed_date IS NULL OR completed_date >= created_date)
        )
        """,
        """
        CREATE TABLE expenses (
            expense_id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL REFERENCES projects(project_id),
            expense_date DATE NOT NULL,
            amount_dollars DECIMAL(12, 2) NOT NULL CHECK (amount_dollars > 0),
            category VARCHAR NOT NULL
                CHECK (category IN ('GPU cloud', 'data labeling', 'software', 'travel')),
            note VARCHAR
        )
        """,
    ]

    _data = mo.notebook_dir() / "data"
    if database.exists():
        database.unlink()
    with duckdb.connect(database) as _con:
        for _statement in create_statements:
            _con.execute(_statement)

        # people reference people, and DuckDB checks each row against the
        # table as it was before the statement, so load one person at a
        # time, managers first (the CSV is written in that order, and every
        # manager_id is smaller than the person_id that reports to it).
        _people_rows = _con.sql(
            f"SELECT * FROM read_csv('{_data}/people.csv') ORDER BY person_id"
        ).fetchall()
        for _row in _people_rows:
            _con.execute(
                "INSERT INTO people VALUES (?, ?, ?, ?, ?, ?, ?)", list(_row)
            )

        for _table in ("projects", "assignments", "tasks", "expenses"):
            _con.execute(
                f"INSERT INTO {_table} SELECT * FROM read_csv('{_data}/{_table}.csv')"
            )

        _con.execute(
            """
            CREATE VIEW project_spend AS
            SELECT
                p.project_id,
                p.project_name,
                p.client,
                p.status,
                p.budget_dollars,
                COALESCE(SUM(e.amount_dollars), 0) AS spent_dollars,
                ROUND(COALESCE(SUM(e.amount_dollars), 0) / p.budget_dollars, 3)
                    AS share_of_budget
            FROM projects AS p
            LEFT JOIN expenses AS e USING (project_id)
            GROUP BY p.project_id, p.project_name, p.client, p.status, p.budget_dollars
            """
        )
    print(f"built {database.name} from {len(create_statements)} tables plus the view")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Data

    `make_data.py`, next to this notebook, writes one CSV per table into `data/`
    with a fixed seed, covering the 12 months up to the `as_of` date
    **2026-11-16**. The data obeys every rule in the scenario, with one
    deliberate exception: the rule that a task's assignee must work on the
    task's project cannot be held by a column constraint, so it is broken on
    purpose in **exactly two rows**, `task_id 249` (project 7, assignee 1) and
    `task_id 250` (project 4, assignee 2). Question 7 in Part B must find
    exactly those two. The first generated draft broke unwritten rules
    (assignees added to tasks created before the person joined the lab), so the
    generator now picks assignees only from people already at the lab on the
    task's created date, and the planted rows are the only violations left.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A Look at the Data

    One CSV read with polars and one column charted: expense dollars by month.
    """)
    return


@app.cell
def _(mo, pl):
    import altair as alt

    expenses_csv = pl.read_csv(
        mo.notebook_dir() / "data" / "expenses.csv", try_parse_dates=True
    )
    _by_month = (
        expenses_csv.with_columns(pl.col("expense_date").dt.strftime("%Y-%m").alias("month"))
        .group_by("month")
        .agg(pl.col("amount_dollars").sum().round(0).alias("dollars"))
        .sort("month")
    )
    spend_chart = (
        alt.Chart(_by_month)
        .mark_bar()
        .encode(
            x=alt.X("month:N", title="month"),
            y=alt.Y("dollars:Q", title="expense dollars"),
        )
        .properties(title="Lab spending by month")
    )
    spend_chart
    return (expenses_csv,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A real lab's spending would look like this: lumpy month to month, heavier in
    recent months as more projects went active. The first draft of
    `make_data.py` put almost everything in the final weeks, which looked like a
    data bug rather than a business, so the generator was changed to spread the
    older expenses across each project's whole life and keep roughly 70 recent
    rows for the 90-day question.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Row Counts
    """)
    return


@app.cell
def _(ask):
    for _table in ("people", "projects", "assignments", "tasks", "expenses"):
        _count = ask(f"SELECT COUNT(*) AS n FROM {_table}")["n"][0]
        print(f"{_table:<12} {_count:>5} rows")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A Row It Refuses

    An expense of −50 dollars breaks `CHECK (amount_dollars > 0)`. The insert
    below uses its own write connection inside `try`/`except`, so the error is
    shown and the rest of the notebook still runs.
    """)
    return


@app.cell
def _(database, duckdb):
    try:
        with duckdb.connect(database) as _con:
            _con.execute(
                "INSERT INTO expenses VALUES (9999, 1, DATE '2026-11-01', -50, 'software', 'refund typo')"
            )
        print("the database accepted the row, which would be a bug")
    except Exception as _error:
        print(f"refused, as designed: {_error}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Answers You Already Knew

    Three queries whose answers were known before running them, each printed
    next to its expected value.
    """)
    return


@app.cell
def _(ask):
    _founders = ask("SELECT COUNT(*) AS n FROM people WHERE manager_id IS NULL")["n"][0]
    print(f"people who report to nobody: {_founders}  (expected 2, the founders)")

    _internal = ask("SELECT COUNT(*) AS n FROM projects WHERE client IS NULL")["n"][0]
    print(f"projects with no client: {_internal}  (expected 3, the internal ones)")

    _max_hours = ask("SELECT MAX(hours_per_week) AS h FROM assignments")["h"][0]
    print(f"largest hours-per-week on one project: {_max_hours}  (expected 25; the rule caps it at 40)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A View

    The weekly question the founders actually ask is "where does each project
    stand against its budget?", so the build cell saves it as the view
    `project_spend`. Part B's question 1 queries this view by name.
    """)
    return


@app.cell
def _(ask):
    ask("SELECT * FROM project_spend ORDER BY share_of_budget DESC")
    return


if __name__ == "__main__":
    app.run()
