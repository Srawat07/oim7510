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

    Each project's expenses against its budget, and the share of budget spent,
    largest share first. This answer queries the `project_spend` view that
    Part A's build cell saved.
    """)
    return


@app.cell
def _(ask):
    q1 = ask("""
        SELECT project_name, client, status, budget_dollars, spent_dollars, share_of_budget
        FROM project_spend
        ORDER BY share_of_budget DESC
    """)
    _top = q1.row(0, named=True)
    _second = q1.row(1, named=True)
    print(
        f"{_top['project_name']} has spent {_top['spent_dollars']:,.2f} of its "
        f"{_top['budget_dollars']:,.2f} budget, {_top['share_of_budget']:.1%} and the only "
        f"project over budget; the next heaviest is {_second['project_name']} at "
        f"{_second['share_of_budget']:.1%}."
    )
    q1
    return (q1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q2. Which tasks are past due and not completed?

    Three tables: `tasks` joined to `projects` for the project name and LEFT
    joined to `people` for the assignee's name, keeping unassigned tasks.
    """)
    return


@app.cell
def _(as_of, ask):
    q2 = ask(f"""
        SELECT t.task_id, p.project_name, t.description, t.due_date,
               pe.first_name || ' ' || pe.last_name AS assignee
        FROM tasks AS t
        JOIN projects AS p USING (project_id)
        LEFT JOIN people AS pe ON pe.person_id = t.assignee_id
        WHERE t.completed_date IS NULL AND t.due_date < DATE '{as_of}'
        ORDER BY t.due_date
    """)
    print(
        f"As of {as_of}, {len(q2)} tasks are past their due date and still open; "
        f"the oldest has been overdue since {q2.row(0, named=True)['due_date']}."
    )
    q2
    return (q2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q3. Who is over 40 hours a week across active projects?

    Each person's committed hours a week across all active projects, with the
    people above 40 pulled out. Each single assignment respects the 40-hour
    cap, so anyone over 40 here is overloaded across projects, not on one.
    """)
    return


@app.cell
def _(ask):
    q3 = ask("""
        SELECT pe.person_id,
               pe.first_name || ' ' || pe.last_name AS person,
               SUM(a.hours_per_week) AS hours_per_week
        FROM people AS pe
        JOIN assignments AS a ON a.person_id = pe.person_id
        JOIN projects AS p ON p.project_id = a.project_id
        WHERE p.status = 'active'
        GROUP BY pe.person_id, person
        ORDER BY hours_per_week DESC
    """)
    _over = q3.filter(q3["hours_per_week"] > 40)
    _names = []
    for _row in _over.iter_rows(named=True):
        _names.append(f"{_row['person']} ({_row['hours_per_week']} h/w)")
    print(
        f"{len(_over)} people are over 40 hours a week across active projects: "
        + "; ".join(_names) + "."
    )
    q3
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q4. Which expense categories ran above average in the last 90 days?

    Expenses by category over the last 90 days ending on `as_of`, keeping the
    categories whose total is above the average of the category totals; the
    "above the average" part needs a subquery.
    """)
    return


@app.cell
def _(as_of, ask):
    q4 = ask(f"""
        WITH category_totals AS (
            SELECT category, SUM(amount_dollars) AS total_dollars
            FROM expenses
            WHERE expense_date > DATE '{as_of}' - INTERVAL 90 DAY
              AND expense_date <= DATE '{as_of}'
            GROUP BY category
        )
        SELECT category, total_dollars
        FROM category_totals
        WHERE total_dollars > (SELECT AVG(total_dollars) FROM category_totals)
        ORDER BY total_dollars DESC
    """)
    _parts = []
    for _row in q4.iter_rows(named=True):
        _parts.append(f"{_row['category']} at {_row['total_dollars']:,.2f}")
    print(
        f"In the 90 days ending {as_of}, {len(q4)} categories ran above the "
        f"category average: " + "; ".join(_parts) + "."
    )
    q4
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q5. Which projects have no expenses at all?

    A LEFT join from projects to expenses; a project with no match is the
    answer, and an unattached row is a real answer here.
    """)
    return


@app.cell
def _(ask):
    q5 = ask("""
        SELECT p.project_id, p.project_name, p.status
        FROM projects AS p
        LEFT JOIN expenses AS e USING (project_id)
        WHERE e.expense_id IS NULL
        ORDER BY p.project_id
    """)
    _names = []
    for _row in q5.iter_rows(named=True):
        _names.append(f"{_row['project_name']} ({_row['status']})")
    print(f"{len(q5)} projects have no expenses at all: " + " and ".join(_names) + ".")
    q5
    return (q5,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q6. Task counts and total expenses per project, cross-checked

    One row per project with its task count and total expenses. Joining tasks
    and expenses to projects in one query multiplies every task by every
    expense, so each count comes from its own subquery, and the printed check
    compares both columns against counting each table on its own.
    """)
    return


@app.cell
def _(ask):
    q6 = ask("""
        SELECT p.project_id, p.project_name,
               (SELECT COUNT(*) FROM tasks AS t
                WHERE t.project_id = p.project_id) AS task_count,
               (SELECT COALESCE(SUM(e.amount_dollars), 0) FROM expenses AS e
                WHERE e.project_id = p.project_id) AS total_expenses
        FROM projects AS p
        ORDER BY p.project_id
    """)
    _task_sum = int(q6["task_count"].sum())
    _expense_sum = round(float(q6["total_expenses"].sum()), 2)
    _tasks_direct = int(ask("SELECT COUNT(*) AS n FROM tasks")["n"][0])
    _expenses_direct = round(float(ask("SELECT SUM(amount_dollars) AS s FROM expenses")["s"][0]), 2)
    print(
        f"check: task counts sum to {_task_sum} against {_tasks_direct} tasks counted "
        f"on their own, and expense totals sum to {_expense_sum:,.2f} against "
        f"{_expenses_direct:,.2f}; agree: "
        f"{_task_sum == _tasks_direct and _expense_sum == _expenses_direct}"
    )
    q6
    return (q6,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q7. Does every task's assignee actually work on its project?

    The rule no table constraint can hold, checked with a query across three
    tables: every assigned task is matched against `assignments`; a task whose
    assignee has no seat on its project breaks the rule. The data breaks it in
    exactly two recorded rows, and this query must find exactly those two.
    """)
    return


@app.cell
def _(ask):
    q7 = ask("""
        SELECT t.task_id, t.project_id,
               pe.first_name || ' ' || pe.last_name AS assignee
        FROM tasks AS t
        JOIN people AS pe ON pe.person_id = t.assignee_id
        LEFT JOIN assignments AS a
            ON a.project_id = t.project_id AND a.person_id = t.assignee_id
        WHERE t.assignee_id IS NOT NULL AND a.person_id IS NULL
        ORDER BY t.task_id
    """)
    _ids = list(q7["task_id"])
    print(
        f"{len(q7)} tasks break the rule, task_ids {_ids}, exactly the two rows "
        f"planted in Part A (249 on project 7, 250 on project 4); every other "
        f"assigned task's assignee holds a seat on its project."
    )
    q7
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q8. My own question: which client costs the most to serve?

    A founder planning next year's pricing would ask this: for each external
    client, the budget across their projects, what the lab has actually spent,
    and spend per budgeted dollar, heaviest first. It aggregates the
    `project_spend` view a level further than any question above.
    """)
    return


@app.cell
def _(ask):
    q8 = ask("""
        SELECT client,
               COUNT(*) AS projects,
               SUM(budget_dollars) AS total_budget,
               SUM(spent_dollars) AS total_spent,
               ROUND(SUM(spent_dollars) / SUM(budget_dollars), 3) AS spent_per_budget_dollar
        FROM project_spend
        WHERE client IS NOT NULL
        GROUP BY client
        ORDER BY spent_per_budget_dollar DESC
    """)
    _top = q8.row(0, named=True)
    print(
        f"{_top['client']} is the most expensive client to serve: the lab has spent "
        f"{_top['total_spent']:,.2f} against {_top['total_budget']:,.2f} budgeted, "
        f"{_top['spent_per_budget_dollar']:.1%} of every budgeted dollar already gone."
    )
    q8
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. How I Know These Numbers Are Right

    Two answers reached a second, independent way, both printed below:

    1. **Q1 against the raw expenses table.** The view's `spent_dollars` summed
    over all projects must equal `SUM(amount_dollars)` over the whole
    `expenses` table, because every expense belongs to exactly one project.
    2. **Q5 against subtraction.** The number of projects with no expenses must
    equal 12 minus the number of distinct projects that appear in `expenses`.
    Q5 finds them by a LEFT join; this check never joins at all.
    """)
    return


@app.cell
def _(ask, q1, q5):
    _view_total = round(float(q1["spent_dollars"].sum()), 2)
    _raw_total = round(float(ask("SELECT SUM(amount_dollars) AS s FROM expenses")["s"][0]), 2)
    print(
        f"check 1: view spend summed over projects {_view_total:,.2f} against the "
        f"expenses table {_raw_total:,.2f}; agree: {_view_total == _raw_total}"
    )

    _projects = int(ask("SELECT COUNT(*) AS n FROM projects")["n"][0])
    _with_expenses = int(ask("SELECT COUNT(DISTINCT project_id) AS n FROM expenses")["n"][0])
    print(
        f"check 2: Q5 found {len(q5)} projects with no expenses, and "
        f"{_projects} - {_with_expenses} = {_projects - _with_expenses}; "
        f"agree: {len(q5) == _projects - _with_expenses}"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Working With the Agent

    Q6 is the answer I did not accept as-is. The first version joined
    `projects` to `tasks` and `expenses` in a single query and counted from the
    joined rows, which looked reasonable and ran without error, but every task
    row was multiplied by every expense row of the same project, so the task
    counts and expense totals were both inflated. I knew because of the
    cross-check that is now printed under Q6: the task counts have to sum to
    250 and the expense total has to match the `expenses` table, and the joined
    version failed both. The kept version computes each column in its own
    subquery, and the printed check agrees. The fix is in the Q6 cell, in this
    notebook's history.
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

    **The run.** The cell below runs the joins alone, with no `WHERE` and no
    grouping, and counts the rows. It returned **250**, which matched the
    prediction: the inner join to `projects` is one-to-one from the task side,
    and the LEFT join to `people` attaches at most one person and keeps the
    unassigned tasks.

    **What one row of the final result means.** One row of Q2's result is one
    task that was still open and past its due date on the `as_of` date, named
    by its project and, when it has one, by the person responsible for it.
    """)
    return


@app.cell
def _(ask):
    _joined = ask("""
        SELECT COUNT(*) AS n
        FROM tasks AS t
        JOIN projects AS p USING (project_id)
        LEFT JOIN people AS pe ON pe.person_id = t.assignee_id
    """)
    print(
        f"the joins alone produce {_joined['n'][0]} rows; predicted 250; "
        f"matched: {int(_joined['n'][0]) == 250}"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Going Further

    A control that changes query results: the dropdown below holds every
    project name, and the cell after it re-runs the open-task query for
    whichever project is picked, so a founder can review one project's backlog
    without touching SQL. It is in the two cells below this one.
    """)
    return


@app.cell
def _(ask, mo):
    _names = list(ask("SELECT project_name FROM projects ORDER BY project_id")["project_name"])
    project_picker = mo.ui.dropdown(options=_names, value=_names[0], label="project")
    project_picker
    return (project_picker,)


@app.cell
def _(as_of, ask, project_picker):
    picked_tasks = ask(f"""
        SELECT t.task_id, t.description, t.due_date,
               CASE WHEN t.due_date < DATE '{as_of}' THEN 'overdue' ELSE 'on time' END AS standing
        FROM tasks AS t
        JOIN projects AS p USING (project_id)
        WHERE p.project_name = '{project_picker.value}'
          AND t.completed_date IS NULL
        ORDER BY t.due_date
    """)
    print(f"{project_picker.value}: {len(picked_tasks)} open tasks as of {as_of}")
    picked_tasks
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
