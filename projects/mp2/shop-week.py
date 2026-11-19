# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo",
# ]
# ///
"""Mini Project 2.
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
    # Mini Project 2: The Shop's Week

    Option B. A Monday-morning report for Northwind Traders' operations manager, built on the course shop API. The data is fetched live each run, so the numbers change with the run day.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    Northwind Traders sells specialty food to shops and restaurants, and orders arrive every day. The operations manager starts each Monday by asking the same five things about the last seven days: how many orders came in, what they were worth, where they are going, which products sold the most, and which orders have not shipped yet. This tool fetches the week's orders from the company's order system and prints that report, so the manager reads one page instead of clicking through order screens.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI

    I opened the API in a browser first and read the replies. `https://oim.zhili.dev/shop/orders?from_date=...&to_date=...` returns an `items` list of orders and a `pagination` block with `total`, `has_next`, and `page`; a page holds 50 orders unless `per_page` asks for up to 100. `https://oim.zhili.dev/shop/orders/20227` returns one order with its `lines`, each line holding `product_name`, `quantity`, and `line_total_dollars`.

    How I would solve it:

    1. Work out the date window: today, and the six days before it, using `date.today()` and `timedelta`.
    2. Write a function that requests `/shop/orders` for that window, page after page, and collects every order into one list.
    3. Write a second function that requests one order's address and returns its lines.
    4. Loop over the orders to count them, add up revenue from the order totals, and total revenue per destination country in a counting dictionary.
    5. Loop over every order's lines to add up units sold per product in another counting dictionary, then take the five largest.
    6. Collect the orders whose `shipped_date` is empty, and print the whole report with aligned f-strings plus one sentence for the manager.

    The functions my tool needs:

    - `fetch_orders(base_url, from_date, to_date)`: takes the API address and the two dates; requests `/shop/orders` with `from_date`, `to_date`, `page`, and `per_page=100`; returns a list of order records.
    - `fetch_order_lines(base_url, order_id)`: takes the address and one order id; requests `/shop/orders/{order_id}`; returns that order's list of line records.
    - `reported_order_count(base_url, from_date, to_date)`: same query, but returns only the `total` the API reports in `pagination`, for the check below.

    How I will know I have every record: keep requesting the next page while the reply says `has_next` is true, then compare the length of my list with the `total` the API reports.

    My section 6 check: the number of orders I fetched should equal the `total` the API's pagination reports, and one order's `order_total_dollars` should equal the sum of its own lines' `line_total_dollars`. Those are the pairs of numbers that should agree.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs

    *Every input in one cell.*
    """)
    return


@app.cell
def _():
    # Inputs go here.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    *The functions and the code that uses them.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    *The result table and the sentence, printed from code.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    *At least one result reached a second way, shown to agree.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    *One piece of AI output not accepted as-is, or how a right-first-time answer was verified.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Reading It Back

    *Two functions explained, and a committed prediction for one input change.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Going Further

    *What was tried past the main task.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. Time Spent

    *About how many hours, as one number.*
    """)
    return


if __name__ == "__main__":
    app.run()
