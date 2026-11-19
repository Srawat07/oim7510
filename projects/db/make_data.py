"""Generate the CSVs for the BabsonAI Labs database (scenario A).

Writes one CSV per table into projects/db/data/. Deterministic: seeded.
The data obeys every scenario rule, except the rule checked by question 7
(a task's assignee must work on the task's project), which is broken on
purpose in exactly two rows; the script prints which rows at the end.

Run from the repository root:  uv run python projects/db/make_data.py
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(7510)

AS_OF = date(2026, 11, 16)
WINDOW_START = AS_OF - timedelta(days=365)
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

FIRST = ["Ava", "Noah", "Mia", "Liam", "Zoe", "Ethan", "Ivy", "Lucas", "Nora", "Owen",
         "Ruth", "Dev", "Sana", "Marco", "Lena", "Hugo", "Priya", "Jonas", "Elif", "Tomas",
         "Keiko", "Omar", "Anna", "Felix", "Dara"]
LAST = ["Stone", "Patel", "Kim", "Rossi", "Chen", "Lopez", "Novak", "Osei", "Haug", "Silva",
        "Meyer", "Khan", "Baker", "Ito", "Weiss", "Moreau", "Rao", "Berg", "Demir", "Valdez",
        "Sato", "Nasser", "Lind", "Vogel", "Quinn"]

# ---------------------------------------------------------------- people
# Two founders report to nobody; three leads report to the founders;
# everyone else reports to a lead. Written managers-first so the
# self-referencing foreign key loads one row at a time without complaint.
people = []
titles_pool = ["ML Engineer", "Data Engineer", "Analyst", "Product Manager", "Designer"]
for pid in range(1, 26):
    first = FIRST[pid - 1]
    last = LAST[pid - 1]
    if pid == 1:
        title, manager = "CEO", None
    elif pid == 2:
        title, manager = "CTO", None
    elif pid <= 5:
        title, manager = "Lead " + random.choice(["Engineer", "Scientist", "Consultant"]), random.choice([1, 2])
    else:
        title, manager = random.choice(titles_pool), random.choice([3, 4, 5])
    if pid <= 5:
        start = date(2023, 1, 1) + timedelta(days=random.randint(0, 400))
    else:
        start = date(2023, 6, 1) + timedelta(days=random.randint(0, 1150))
    start = min(start, AS_OF - timedelta(days=30))
    email = f"{first.lower()}.{last.lower()}@babsonailabs.com"
    people.append({"person_id": pid, "first_name": first, "last_name": last,
                   "work_email": email, "title": title,
                   "start_date": start.isoformat(),
                   "manager_id": "" if manager is None else manager})

# ---------------------------------------------------------------- projects
CLIENTS = ["Harborline Insurance", "Beacon Retail Group", "Mass Medical Partners",
           "Charles River Freight", "Bluebird Hotels", "Granite Peak Capital",
           "Fenway Foods", "Northstar Legal", "Comet Logistics"]
CATEGORIES = ["LLM app", "data pipeline", "internal tool"]
STATUSES = ["active"] * 6 + ["paused"] * 2 + ["done"] * 2 + ["planned"] * 2
PROJECT_NAMES = ["Atlas", "Beacon", "Cascade", "Delta", "Ember", "Flint",
                 "Granite", "Harbor", "Ivory", "Juniper", "Kestrel", "Lumen"]

projects = []
for i, status in enumerate(STATUSES, start=1):
    internal = i in (3, 7, 11)
    if status == "planned":
        start = AS_OF + timedelta(days=random.randint(10, 60))
    elif status == "done":
        start = WINDOW_START + timedelta(days=random.randint(0, 60))
    else:
        start = WINDOW_START + timedelta(days=random.randint(0, 240))
    budget = random.choice([25000, 40000, 60000, 90000, 120000, 180000, 250000, 400000])
    if i == 6:
        budget = 30000  # deliberately small budget; this project will overspend
    projects.append({"project_id": i, "project_name": "Project " + PROJECT_NAMES[i - 1],
                     "client": "" if internal else CLIENTS[(i - 1) % len(CLIENTS)],
                     "category": CATEGORIES[i % 3],
                     "budget_dollars": budget,
                     "start_date": start.isoformat(),
                     "status": status})

# ---------------------------------------------------------------- assignments
ROLES = ["engineer", "analyst", "reviewer", "project lead", "designer"]
assignments = []
members = {}
for proj in projects:
    pid = proj["project_id"]
    team_size = 2 if proj["status"] == "planned" else random.randint(3, 6)
    team = random.sample(range(1, 26), team_size)
    if pid in (2, 4, 6) and 5 not in team:
        team[0] = 5  # person 5 sits on three active projects, 15 h/w each: over 40 in total
    members[pid] = []
    proj_start = date.fromisoformat(proj["start_date"])
    for person_id in team:
        person_start = date.fromisoformat(people[person_id - 1]["start_date"])
        joined = max(proj_start, person_start) + timedelta(days=random.randint(0, 20))
        joined = min(joined, AS_OF)
        hours = 15 if person_id == 5 else random.randint(5, 25)
        assignments.append({"person_id": person_id, "project_id": pid,
                            "role": random.choice(ROLES), "hours_per_week": hours,
                            "joined_date": joined.isoformat()})
        members[pid].append(person_id)

# ---------------------------------------------------------------- tasks
VERBS = ["Draft", "Review", "Ship", "Test", "Document", "Refactor", "Design", "Benchmark"]
THINGS = ["ingestion job", "eval harness", "client demo", "prompt set", "dashboard",
          "schema", "retrieval index", "cost report", "release notes", "onboarding doc"]
task_projects = [p for p in projects if p["status"] != "planned"]
tasks = []
for task_id in range(1, 251):
    proj = random.choice(task_projects)
    proj_start = date.fromisoformat(proj["start_date"])
    latest = min(AS_OF, proj_start + timedelta(days=330))
    span = (latest - proj_start).days
    created = proj_start + timedelta(days=random.randint(0, max(span, 1)))
    due = created + timedelta(days=random.randint(3, 30))
    assignee = ""
    if random.random() > 0.15:
        eligible = []
        for m in members[proj["project_id"]]:
            if date.fromisoformat(people[m - 1]["start_date"]) <= created:
                eligible.append(m)
        if eligible:
            assignee = random.choice(eligible)
    completed = ""
    if random.random() < 0.6:
        horizon = (AS_OF - created).days
        if horizon > 0:
            completed = (created + timedelta(days=random.randint(1, min(horizon, 45)))).isoformat()
    tasks.append({"task_id": task_id, "project_id": proj["project_id"],
                  "description": f"{random.choice(VERBS)} the {random.choice(THINGS)}",
                  "created_date": created.isoformat(),
                  "assignee_id": assignee,
                  "due_date": due.isoformat(),
                  "completed_date": completed})

# Break the question-7 rule in exactly two rows: tasks 249 and 250 get an
# assignee who does not work on the task's project (start date still fine).
violations = []
for task in (tasks[248], tasks[249]):
    proj_members = members[task["project_id"]]
    created = date.fromisoformat(task["created_date"])
    outsiders = []
    for p in people:
        if p["person_id"] not in proj_members and date.fromisoformat(p["start_date"]) <= created:
            outsiders.append(p["person_id"])
    task["assignee_id"] = outsiders[0]
    violations.append((task["task_id"], task["project_id"], task["assignee_id"]))

# ---------------------------------------------------------------- expenses
EXPENSE_RANGES = {"GPU cloud": (200, 6000), "data labeling": (100, 3000),
                  "software": (50, 1500), "travel": (100, 2500)}
expense_projects = [p for p in projects if p["status"] != "planned"]
expenses = []
for expense_id in range(1, 161):
    if expense_id <= 70:
        proj = random.choice(expense_projects)
        day = AS_OF - timedelta(days=random.randint(0, 89))
        proj_start = date.fromisoformat(proj["start_date"])
        if day < proj_start:
            day = proj_start + timedelta(days=random.randint(0, 30))
    else:
        proj = random.choice(expense_projects)
        proj_start = date.fromisoformat(proj["start_date"])
        span = (AS_OF - proj_start).days
        day = proj_start + timedelta(days=random.randint(0, max(span, 1)))
    category = random.choice(list(EXPENSE_RANGES))
    low, high = EXPENSE_RANGES[category]
    amount = round(random.uniform(low, high), 2)
    if proj["project_id"] == 6:
        amount = round(amount * 2.5, 2)  # the small-budget project overspends
    expenses.append({"expense_id": expense_id, "project_id": proj["project_id"],
                     "expense_date": day.isoformat(),
                     "amount_dollars": amount,
                     "category": category,
                     "note": f"{category} for project {proj['project_id']}"})

# ---------------------------------------------------------------- write
def write(name, rows):
    with open(DATA_DIR / name, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {name}: {len(rows)} rows")

write("people.csv", people)
write("projects.csv", projects)
write("assignments.csv", assignments)
write("tasks.csv", tasks)
write("expenses.csv", expenses)

overdue_open = 0
for t in tasks:
    if t["completed_date"] == "" and date.fromisoformat(t["due_date"]) < AS_OF:
        overdue_open += 1
print(f"overdue and not completed as of {AS_OF}: {overdue_open} tasks")
print("rule broken on purpose (assignee not on the project) in exactly these rows:")
for task_id, project_id, assignee_id in violations:
    print(f"  task_id {task_id} on project {project_id}, assignee person_id {assignee_id}")
