from pulp import *

# Define the problem
prob = LpProblem("BMC_Transshipment_Problem", LpMinimize)

# Define sets
ports = ["Newark", "Jacksonville"]
intermediate_nodes = ["Boston", "Columbus", "Atlanta", "Richmond", "Mobile"]
distributors = ["Boston", "Columbus", "Atlanta", "Richmond", "Mobile"]

# Supply and demand
supply = {"Newark": 200, "Jacksonville": 300}
demand = {"Boston": 100, "Columbus": 60, "Atlanta": 170, "Richmond": 80, "Mobile": 70}

# Define routes and costs
routes_port_to_intermediate = {
    ("Newark", "Boston"): 30,
    ("Newark", "Richmond"): 40,
    ("Jacksonville", "Atlanta"): 45,
    ("Jacksonville", "Richmond"): 50,
    ("Jacksonville", "Mobile"): 50
}

routes_intermediate_to_distributor = {
    ("Boston", "Boston"): 0,
    ("Columbus", "Columbus"): 0,
    ("Atlanta", "Atlanta"): 0,
    ("Richmond", "Richmond"): 0,
    ("Mobile", "Mobile"): 0,
    ("Boston", "Columbus"): 50,
    ("Columbus", "Atlanta"): 35,
    ("Atlanta", "Columbus"): 40,
    ("Atlanta", "Mobile"): 45,
    ("Atlanta", "Richmond"): 30,
    ("Mobile", "Atlanta"): 25,
}

# Decision variables (Corrected: Use only existing routes)
shipments_port_to_intermediate = LpVariable.dicts("Ship_Port_to_Int",
                                                  ((p, i) for p in ports for i in intermediate_nodes if (p, i) in routes_port_to_intermediate), 0)

shipments_intermediate_to_distributor = LpVariable.dicts("Ship_Int_to_Dist",
                                                         ((i, d) for i in intermediate_nodes for d in distributors if (i, d) in routes_intermediate_to_distributor), 0)



# Objective function
prob += lpSum([routes_port_to_intermediate[p, i] * shipments_port_to_intermediate[p, i] for p, i in shipments_port_to_intermediate]) + \
        lpSum([routes_intermediate_to_distributor[i, d] * shipments_intermediate_to_distributor[i, d] for i, d in shipments_intermediate_to_distributor]), "Total_Transportation_Cost"


# Constraints
# 1. Supply constraints
for p in ports:
    prob += lpSum([shipments_port_to_intermediate[p, i] for i in intermediate_nodes if (p, i) in routes_port_to_intermediate and p==p]) <= supply[p], f"Supply_Constraint_{p}"

# 2. Demand constraints
for d in distributors:
    prob += lpSum([shipments_intermediate_to_distributor[i, d] for i in intermediate_nodes if (i, d) in routes_intermediate_to_distributor and d==d]) == demand[d], f"Demand_Constraint_{d}"

# 3. Transshipment constraints
for i in intermediate_nodes:
    # Inflow (from ports)
    inflow = lpSum([shipments_port_to_intermediate[p, i] for p in ports if (p, i) in routes_port_to_intermediate and i==i])
    # Outflow (to distributors)
    outflow = lpSum([shipments_intermediate_to_distributor[i, d] for d in distributors if (i, d) in routes_intermediate_to_distributor and i==i])
    prob += inflow == outflow, f"Transshipment_Constraint_{i}"

prob.solve()

print("Status:", LpStatus[prob.status])
print("Optimal Transportation Plan:")

for p, i in shipments_port_to_intermediate:
    if shipments_port_to_intermediate[p, i].varValue > 0:
        print(f"Ship {shipments_port_to_intermediate[p, i].varValue} cars from {p} to {i}")

for i, d in shipments_intermediate_to_distributor:
    if shipments_intermediate_to_distributor[i, d].varValue > 0:
        print(f"Ship {shipments_intermediate_to_distributor[i, d].varValue} cars from {i} to {d}")

print("Total Transportation Cost:", value(prob.objective))