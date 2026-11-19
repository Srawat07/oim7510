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
    # Mini Project 1: Two Mortgages, Side by Side

    Option A, a loan repayment schedule. Built in the course starter shape; the headings are the starter's, the work is mine.
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
    """)
    return


@app.cell
def _():
    loan_amount = 400000
    annual_rates = {30: 0.0703, 15: 0.0642}
    return annual_rates, loan_amount


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Two pieces: the payment formula, and the schedule builder that walks the balance down month by month. Interest is rounded to the cent every month, and the last payment is whatever clears the balance exactly.
    """)
    return


@app.cell
def _():
    def monthly_payment(amount, annual_rate, years):
        r = annual_rate / 12
        n = years * 12
        if r == 0:
            return round(amount / n, 2)
        return round(amount * r / (1 - (1 + r) ** -n), 2)

    return (monthly_payment,)


@app.cell
def _(monthly_payment):
    def build_schedule(amount, annual_rate, years):
        r = annual_rate / 12
        n = years * 12
        payment = monthly_payment(amount, annual_rate, years)
        rows = []
        balance = amount
        for month in range(1, n + 1):
            interest = round(balance * r, 2)
            if month < n:
                principal = round(payment - interest, 2)
                paid = payment
            else:
                principal = balance
                paid = round(interest + principal, 2)
            balance = round(balance - principal, 2)
            rows.append((month, paid, interest, principal, balance))
        return rows

    def total_interest(rows):
        total = 0.0
        for row in rows:
            total = round(total + row[2], 2)
        return total

    return build_schedule, total_interest


@app.cell
def _(annual_rates, build_schedule, loan_amount, monthly_payment, total_interest):
    payment_30 = monthly_payment(loan_amount, annual_rates[30], 30)
    payment_15 = monthly_payment(loan_amount, annual_rates[15], 15)
    schedule_30 = build_schedule(loan_amount, annual_rates[30], 30)
    schedule_15 = build_schedule(loan_amount, annual_rates[15], 15)
    total_interest_30 = total_interest(schedule_30)
    total_interest_15 = total_interest(schedule_15)
    return (
        payment_15,
        payment_30,
        schedule_15,
        schedule_30,
        total_interest_15,
        total_interest_30,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    The 30 year loan costs $2,669.27 a month and $560,942.03 in interest over its life. The 15 year loan costs $3,466.86 a month, which is $797.59 more each month, but its total interest is $224,035.34, so my friend pays $336,906.69 less in interest for carrying the higher payment. The full schedules are printed below; the answer sentence is also printed from code, so it changes if the inputs do.
    """)
    return


@app.cell
def _(payment_15, payment_30, schedule_15, schedule_30, total_interest_15, total_interest_30):
    for _years, _payment, _schedule, _total in (
        (30, payment_30, schedule_30, total_interest_30),
        (15, payment_15, schedule_15, total_interest_15),
    ):
        print(f"{_years}-year loan at the input rate: payment {_payment:,.2f} per month")
        print(f"{'month':>5} {'payment':>12} {'interest':>12} {'principal':>12} {'balance':>14}")
        for _row in _schedule:
            print(
                f"{_row[0]:>5} {_row[1]:>12,.2f} {_row[2]:>12,.2f} "
                f"{_row[3]:>12,.2f} {_row[4]:>14,.2f}"
            )
        print(f"total interest over the life of the loan: {_total:,.2f}")
        print()

    _monthly_gap = round(payment_15 - payment_30, 2)
    _interest_gap = round(total_interest_30 - total_interest_15, 2)
    print(
        f"The 15-year loan costs {_monthly_gap:,.2f} more per month than the 30-year loan "
        f"but saves {_interest_gap:,.2f} in total interest "
        f"({total_interest_15:,.2f} against {total_interest_30:,.2f})."
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    Two independent checks, both printed below:

    1. **Principal sums to the loan.** Adding the principal column of each schedule, cent by cent, gives exactly 400,000.00 for both loans, which is the amount borrowed. The schedule and the loan amount agree, and both final balances are exactly 0.00.
    2. **An input whose answer I know without code.** A $120,000 loan over 10 years at 0% interest must cost exactly $1,000.00 a month and $0.00 in interest. The same functions produce exactly that.
    """)
    return


@app.cell
def _(build_schedule, loan_amount, monthly_payment, schedule_15, schedule_30, total_interest):
    for _label, _schedule in (("30-year", schedule_30), ("15-year", schedule_15)):
        _principal_sum = 0.0
        for _row in _schedule:
            _principal_sum = round(_principal_sum + _row[3], 2)
        _final_balance = _schedule[-1][4]
        _agrees = _principal_sum == float(loan_amount) and _final_balance == 0.0
        print(
            f"check 1, {_label}: principal paid sums to {_principal_sum:,.2f} "
            f"against loan amount {loan_amount:,.2f}; final balance {_final_balance:,.2f}; "
            f"agree: {_agrees}"
        )

    _zero_rate = build_schedule(120000, 0.0, 10)
    _zero_payment = monthly_payment(120000, 0.0, 10)
    _zero_interest = total_interest(_zero_rate)
    print(
        f"check 2, known answer: 120,000 over 10 years at 0% gives payment "
        f"{_zero_payment:,.2f} (expected 1,000.00) and total interest "
        f"{_zero_interest:,.2f} (expected 0.00); final balance {_zero_rate[-1][4]:,.2f}"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    The schedule loop in section 4 is the piece I did not accept as-is. The straightforward version my agent and I started from kept the running balance unrounded and only rounded for display, and it also charged the fixed payment in the final month. Walked forward that way, the balance does not land on zero; it ends a few cents off, because real payments are made in cents. I had the loop changed to round interest and principal to the cent every month and to make the final payment exactly interest plus the remaining balance. I knew the fix was right because of the section 6 check: after the change, the principal column sums to exactly 400,000.00 and the final balance is exactly 0.00 for both loans. The change is in the `build_schedule` cell in section 4, committed in this notebook's history.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further

    Two steps past the main task, both below:

    1. **An extra $200 every month.** A second schedule builder accepts an extra payment and stops when the balance hits zero. On the 30 year loan the extra $200 pays it off in 291 months instead of 360, 69 months early, and saves $127,538.86 of interest. On the 15 year loan it finishes 15 months early and saves $21,939.64. The same dollars work much harder against the longer, higher-rate loan.
    2. **A slider.** `mo.ui.slider` lets my friend drag the extra payment from $0 to $1,000 and watch the payoff time and interest saved change, without touching the code.
    """)
    return


@app.cell
def _(monthly_payment):
    def build_with_extra(amount, annual_rate, years, extra):
        r = annual_rate / 12
        payment = monthly_payment(amount, annual_rate, years)
        rows = []
        balance = amount
        month = 0
        while balance > 0:
            month = month + 1
            interest = round(balance * r, 2)
            principal = round(payment + extra - interest, 2)
            paid = round(payment + extra, 2)
            if principal >= balance:
                principal = balance
                paid = round(interest + principal, 2)
            balance = round(balance - principal, 2)
            rows.append((month, paid, interest, principal, balance))
        return rows

    return (build_with_extra,)


@app.cell
def _(annual_rates, build_with_extra, loan_amount, total_interest, total_interest_15, total_interest_30):
    for _years, _base_months, _base_interest in ((30, 360, total_interest_30), (15, 180, total_interest_15)):
        _rows = build_with_extra(loan_amount, annual_rates[_years], _years, 200)
        _interest = total_interest(_rows)
        print(
            f"{_years}-year loan with an extra 200.00/month: paid off in {len(_rows)} months "
            f"({_base_months - len(_rows)} early), interest {_interest:,.2f}, "
            f"saving {round(_base_interest - _interest, 2):,.2f}"
        )
    return


@app.cell
def _(mo):
    extra_slider = mo.ui.slider(0, 1000, step=50, value=200, label="extra payment per month ($)")
    extra_slider
    return (extra_slider,)


@app.cell
def _(annual_rates, build_with_extra, extra_slider, loan_amount, total_interest, total_interest_30):
    _rows = build_with_extra(loan_amount, annual_rates[30], 30, extra_slider.value)
    _interest = total_interest(_rows)
    print(
        f"30-year loan with an extra {extra_slider.value:,.2f}/month: "
        f"paid off in {len(_rows)} months, interest {_interest:,.2f}, "
        f"saving {round(total_interest_30 - _interest, 2):,.2f}"
    )
    return


if __name__ == "__main__":
    app.run()
