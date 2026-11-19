# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo",
# ]
# ///
"""Database Project, Part B: questions and verification."""

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

    return (duckdb,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Part B: Eight Questions for BabsonAI Labs

    Answered against the database that `build.py` builds. One `as_of` date
    drives every date window, in the cell below.
    """)
    return


@app.cell
def _():
    as_of = "2026-11-16"
    return (as_of,)


@app.cell
def _(duckdb, mo):
    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return (ask,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q1. Where does each project stand against its budget?

    *Answered after the prediction commit.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q2. Which tasks are past due and not completed?

    *Answered after the prediction commit.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q3. Who is over 40 hours a week across active projects?

    *Answered after the prediction commit.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q4. Which expense categories ran above average in the last 90 days?

    *Answered after the prediction commit.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q5. Which projects have no expenses at all?

    *Answered after the prediction commit.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q6. Task counts and total expenses per project, cross-checked

    *Answered after the prediction commit.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q7. Does every task's assignee actually work on its project?

    *Answered after the prediction commit.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q8. My own question: which client costs the most to serve?

    *Answered after the prediction commit.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. How I Know These Numbers Are Right

    *Two answers reached a second way, after the answers exist.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Working With the Agent

    *Filled in after the answers exist.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Reading It Back

    The question I picked before answering anything: **Q2, tasks past due and
    not completed, with project name and assignee name.** It joins three
    tables: `tasks`, `projects`, and `people`.

    **My prediction, before running the joins.** The joins alone, before any
    `WHERE` or grouping, will produce **exactly 250 rows**. Reasoning: every
    one of the 250 tasks has exactly one project, so the inner join to
    `projects` keeps the row count at 250, one row per task. The join to
    `people` is a LEFT join on `assignee_id`; a task has at most one assignee
    and unassigned tasks must survive as NULLs, so it neither multiplies nor
    drops rows. 250 in, 250 out.

    *The run and whether it matched: recorded below after the prediction was
    committed.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Going Further

    *Filled in after the answers exist.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Time Spent

    About 6 hours outside class, Parts A and B together.
    """)
    return


if __name__ == "__main__":
    app.run()
