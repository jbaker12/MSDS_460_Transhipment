from pulp import *
import pandas as pd

data = pd.read_excel("project-plan-v003.xlsx")

# print(data)

task_names = data['taskID'].tolist()
task_names = [task for task in task_names if task != 'D']

predecessors = {row['taskID']: str(row['predecessorTaskIDs']).split(', ') if pd.notna(row['predecessorTaskIDs']) else [] for _, row in data.iterrows()}
predecessors = {task: preds for task, preds in predecessors.items() if task != 'D'}
predecessors['B'] = ['A']

durations = {row['taskID']: {'best': row['bestCaseHours'], 'expected': row['expectedHours'], 'worst': row['worstCaseHours']} for _, row in data.iterrows()}
durations = {task: dur for task, dur in durations.items() if task != 'D'}

print(task_names)
print(predecessors)
print(durations)

scenarios = ['best', 'expected', 'worst']

for scenario in scenarios:
    prob = LpProblem(f"Project_Plan_Optimization_{scenario}", LpMinimize)

    # Decision variables (start times for each task)
    start_times = LpVariable.dicts("Start_Time", task_names, 0)

    # Objective function (minimize timespan)
    prob += start_times['H'] - start_times['A']

    for task in task_names:
        for predecessor in predecessors[task]:
            # A task's start time must be greater than or equal to its predecessor's finish time
            prob += start_times[task] >= start_times[predecessor] + durations[predecessor][scenario]

    # Solve the problem
    prob.solve()

    # Print results
    print(f"--- {scenario.upper()} CASE ---")
    print("Status:", LpStatus[prob.status])

    if prob.status == LpStatusOptimal:
        print("Optimal project schedule:")
        for task in task_names:
            print(f"{task}: Start Time = {start_times[task].varValue}")
        print(f"Makespan (Total Project Time) = {value(prob.objective) + durations['H'][scenario]}")

        # Identify the critical path (tasks with zero slack)
        slack = {}

        # Calculate slack for each task
        for task in task_names:
            if predecessors[task] and all(p in task_names for p in predecessors[task]):
                # Earliest Finish Time = Predecessor Finish Time + Duration of current task
                predecessor_finish_time = max(
                    [start_times[p].varValue + durations[p][scenario] for p in predecessors[task]]
                )
                # Slack = Earliest Start - Required Start Time
                slack[task] = start_times[task].varValue - predecessor_finish_time
            else:
                # Tasks with no dependencies have zero slack if they start immediately
                slack[task] = 0

        # Identify tasks with zero slack ( Path)
        print("\nCritical Path:")
        critical_path = [task for task in task_names if slack[task] == 0]
        print(critical_path)


    else:
        print("No optimal solution found.")
    print("\n")
