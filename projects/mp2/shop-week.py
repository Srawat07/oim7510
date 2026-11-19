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

    Every input in one cell, so changing one changes every result after it. `days = 7` means today and the six days before it.
    """)
    return


@app.cell
def _():
    days = 7
    base_url = "https://oim.zhili.dev"
    return base_url, days


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Three functions fetch the data: one pages through the week's orders, one gets a single order's lines, and one asks the API how many orders it has for the window, for the section 6 check. Everything after them is plain Python.
    """)
    return


@app.cell
def _():
    import json

    import requests
    from datetime import date, timedelta

    return date, json, requests, timedelta


@app.cell
def _(date, days, timedelta):
    to_date = date.today()
    from_date = to_date - timedelta(days=days - 1)
    return from_date, to_date


@app.cell
def _(requests):
    def fetch_orders(base, start, end):
        orders = []
        page = 1
        while True:
            reply = requests.get(
                f"{base}/shop/orders",
                params={
                    "from_date": str(start),
                    "to_date": str(end),
                    "per_page": 100,
                    "page": page,
                },
                timeout=30,
            )
            data = reply.json()
            for order in data["items"]:
                orders.append(order)
            if not data["pagination"]["has_next"]:
                break
            page = page + 1
        return orders

    def fetch_order_lines(base, order_id):
        reply = requests.get(f"{base}/shop/orders/{order_id}", timeout=30)
        return reply.json()["lines"]

    def reported_order_count(base, start, end):
        reply = requests.get(
            f"{base}/shop/orders",
            params={"from_date": str(start), "to_date": str(end), "per_page": 1},
            timeout=30,
        )
        return reply.json()["pagination"]["total"]

    return fetch_order_lines, fetch_orders, reported_order_count


@app.cell
def _(base_url, fetch_order_lines, fetch_orders, from_date, to_date):
    orders = fetch_orders(base_url, from_date, to_date)
    lines_by_order = {}
    for _order in orders:
        lines_by_order[_order["order_id"]] = fetch_order_lines(base_url, _order["order_id"])
    return lines_by_order, orders


@app.cell
def _():
    def largest_first(counts):
        rows = []
        remaining = dict(counts)
        while remaining:
            best = None
            for key in remaining:
                if best is None or remaining[key] > remaining[best]:
                    best = key
            rows.append((best, remaining[best]))
            del remaining[best]
        return rows

    return (largest_first,)


@app.cell
def _(largest_first, lines_by_order, orders):
    order_count = len(orders)

    revenue = 0.0
    revenue_by_country = {}
    for _order in orders:
        revenue = round(revenue + _order["order_total_dollars"], 2)
        _country = _order["ship_country"]
        revenue_by_country[_country] = round(
            revenue_by_country.get(_country, 0.0) + _order["order_total_dollars"], 2
        )
    country_rows = largest_first(revenue_by_country)

    units_by_product = {}
    for _order_lines in lines_by_order.values():
        for _line in _order_lines:
            _name = _line["product_name"]
            units_by_product[_name] = units_by_product.get(_name, 0) + _line["quantity"]
    top_products = largest_first(units_by_product)[:5]

    unshipped = []
    for _order in orders:
        if _order["shipped_date"] is None:
            unshipped.append(_order)

    return country_rows, order_count, revenue, top_products, unshipped


@app.cell
def _(json, lines_by_order, mo, orders):
    _data_dir = mo.notebook_dir() / "data"
    _data_dir.mkdir(exist_ok=True)
    _saved = []
    for _order in orders:
        _record = dict(_order)
        _record["lines"] = lines_by_order[_order["order_id"]]
        _saved.append(_record)
    with open(_data_dir / "orders.json", "w") as _file:
        json.dump(_saved, _file, indent=2)
    print(f"saved {len(_saved)} orders with their lines to data/orders.json")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    The report below is printed from code, so every number, and the sentence for the manager, changes with the run day.
    """)
    return


@app.cell
def _(country_rows, from_date, order_count, revenue, to_date, top_products, unshipped):
    print(f"THE SHOP'S WEEK: {from_date} to {to_date}")
    print()
    print(f"orders placed: {order_count}")
    print(f"revenue (order totals, freight not included): {revenue:>12,.2f}")
    print()
    print("revenue by destination country")
    print(f"{'country':<16} {'revenue':>12}")
    for _country, _amount in country_rows:
        print(f"{_country:<16} {_amount:>12,.2f}")
    print()
    print("five best-selling products by units")
    print(f"{'product':<34} {'units':>6}")
    for _product, _units in top_products:
        print(f"{_product:<34} {_units:>6}")
    print()
    print("orders not yet shipped")
    print(f"{'order':>6} {'customer':<32} {'country':<14} {'total':>12}")
    for _order in unshipped:
        print(
            f"{_order['order_id']:>6} {_order['customer_name']:<32} "
            f"{_order['ship_country']:<14} {_order['order_total_dollars']:>12,.2f}"
        )
    print()
    _top_country = country_rows[0]
    _top_product = top_products[0]
    print(
        f"In the week ending {to_date}, Northwind took {order_count} orders worth "
        f"{revenue:,.2f} before freight; {_top_country[0]} was the largest market at "
        f"{_top_country[1]:,.2f}, {_top_product[0]} led with {_top_product[1]} units, "
        f"and {len(unshipped)} orders are still waiting to ship."
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    Two checks, printed below:

    1. **Count against the API's own count.** My list of fetched orders should be exactly as long as the `total` the API reports in its pagination block for the same window. If a page were ever dropped, these two would disagree.
    2. **One order against its own lines.** The largest order's `order_total_dollars` should equal the sum of its lines' `line_total_dollars`, added cent by cent. They agree, which also shows the order total leaves freight out, so my revenue number excludes freight as the manager asked.
    """)
    return


@app.cell
def _(base_url, from_date, lines_by_order, orders, reported_order_count, to_date):
    _reported = reported_order_count(base_url, from_date, to_date)
    print(
        f"check 1: fetched {len(orders)} orders; the API reports {_reported} "
        f"for the same window; agree: {len(orders) == _reported}"
    )

    if orders:
        _biggest = orders[0]
        for _order in orders:
            if _order["order_total_dollars"] > _biggest["order_total_dollars"]:
                _biggest = _order
        _line_sum = 0.0
        for _line in lines_by_order[_biggest["order_id"]]:
            _line_sum = round(_line_sum + _line["line_total_dollars"], 2)
        print(
            f"check 2: order {_biggest['order_id']} total is "
            f"{_biggest['order_total_dollars']:,.2f}; its {len(lines_by_order[_biggest['order_id']])} "
            f"lines sum to {_line_sum:,.2f}; freight ({_biggest['freight_dollars']:,.2f}) is separate; "
            f"agree: {_line_sum == _biggest['order_total_dollars']}"
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    The fetch function is the piece I did not accept as-is. The first version requested only page one of `/shop/orders`. With `per_page=100` and this week's order volume it happened to return everything, which is exactly the kind of bug that hides: it works until a busy week has more than one page, then silently under-reports the whole Monday report. I had it changed to keep requesting while the reply's `has_next` is true, and I added check 1 in section 6 so the notebook itself proves the list is complete on every run, not just this one. The change is the `while True` loop in the `fetch_orders` cell in section 4, and the proof is the section 6 printout.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Reading It Back

    **Two functions, in my own words.**

    - `fetch_orders(base, start, end)`: in go the API's address and the first and last day of the window; out comes one flat list of order records, however many pages the API split them across. The line I had to ask about was `params={...}` in `requests.get`: it builds the `?from_date=...&page=...` part of the address for me, with the values escaped, instead of me gluing strings together.
    - `fetch_order_lines(base, order_id)`: in go the address and one order's id; out comes that order's list of line records. The line I asked about was `reply.json()["lines"]`: `.json()` turns the reply's text into dictionaries and lists, and `"lines"` picks the nested list out of the order record.

    **My prediction, committed before the change.** The change: `days` in Inputs from 7 to 14. On today's 7-day run the tool fetched 22 orders worth 826,504.02. A 14-day window contains the 7-day window, so I expect every one of those 22 orders to still be in the list, the order count to land somewhere near twice 22, in the 35 to 50 range, and revenue to grow by a similar factor. The two section 6 checks should still both agree, since neither depends on the window's length.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Going Further

    Revenue by day, as a chart. The cell below groups the week's orders by order date and draws a bar per day with altair (added to the project with `uv add`, imported only here). The shape answers something the totals hide: whether the week's money arrived evenly or in bursts, which is what the manager would ask next.
    """)
    return


@app.cell
def _(orders):
    import altair as alt
    import polars as pl

    _revenue_by_day = {}
    for _order in orders:
        _day = _order["order_date"][:10]
        _revenue_by_day[_day] = round(
            _revenue_by_day.get(_day, 0.0) + _order["order_total_dollars"], 2
        )
    _days_sorted = sorted(_revenue_by_day)
    _chart_data = pl.DataFrame(
        {
            "day": _days_sorted,
            "revenue": [_revenue_by_day[_d] for _d in _days_sorted],
        }
    )
    revenue_chart = (
        alt.Chart(_chart_data)
        .mark_bar()
        .encode(
            x=alt.X("day:N", title="order date"),
            y=alt.Y("revenue:Q", title="revenue (dollars, before freight)"),
        )
        .properties(title="Revenue by day, last seven days")
    )
    revenue_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. Time Spent

    About 4 hours outside class.
    """)
    return


if __name__ == "__main__":
    app.run()
