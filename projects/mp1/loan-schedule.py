# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo",
# ]
# ///
"""Mini Project 1.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mini Project 1

    Your choice of option, what each one asks for, the due date and how it is graded are on the Mini Project 1 page of the course site, linked from the calendar. This notebook is the shape to build it in. Keep the headings, and replace each line in italics with your own.

    Save it in your course repository as `projects/mp1/<your-tool>.py`, named for what it does, such as `loan-schedule.py`, and open it with `uv run marimo edit`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    A friend is buying a $500,000 condo with 20% down, so she needs a $400,000 mortgage. She has two rates from the national weekly averages, a 30 year loan at 7.03% and a 15 year loan at 6.42%, and she wants to see the two loans side by side before her lender's own quote arrives. This tool shows her the monthly payment, the full month by month payoff schedule, and the total interest for each loan, so she can decide which term fits her budget, and she can change the rates when the real quote comes in.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI

    How I would solve it, before asking the agent anything:

    1. Work out the monthly payment for each term with the loan formula from the assignment page, using the annual rate divided by 12 and the number of months.
    2. For each loan, start from the full balance and walk month by month: this month's interest is the balance times the monthly rate, the principal paid is the payment minus that interest, and the new balance is the old balance minus the principal.
    3. Round interest and payments to the cent every month, so the table matches what a bank statement would show.
    4. Make the final month's payment whatever amount brings the balance to exactly zero, instead of the fixed payment.
    5. Add up the interest column for each loan, then compare the two totals in one sentence for my friend.

    - My loop carries the remaining balance from one month into the next, the way a running total carries its sum. Everything else in a row (interest, principal) is computed from that balance.
    - My section 6 check: the principal column of each schedule should add up to exactly 400,000.00. The sum of principal paid and the amount borrowed are the two numbers that should agree, for both loans.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs

    Every number the project starts from goes in the cell below, and nowhere else, so that changing one input changes every result after it.

    Copy in the default inputs for your option from the Mini Project 1 page. If you chose D, your own option, type your data in here, or ask your agent to generate it with `faker`. The required part reads no file.
    """)
    return


@app.cell
def _():
    # Your inputs.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Add as many cells as you need. Try each step yourself before you ask your agent, and commit as you go.
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    *A table of your results in the cell below, printed with `print` and f-strings, then one sentence here that answers the question in section 1, with the number in it.*
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    *At least one check that reaches a result a second, independent way. Name what you compared and what came out.*
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    *Pick one piece of AI output you did not accept as-is. What did it give you, what did you change, and how did you know? Point to the commit or the cell.*

    *If the agent got it right the first time: what did you do to verify that?*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further

    *Take at least one step past the main task, in any direction, and use your agent as much as you like. It does not have to work. State what you tried, what you found, and where it is in this notebook.*
    """)
    return


if __name__ == "__main__":
    app.run()
