def process_formula(arrays):
    # Step 1: Group arrays by their sorted unique absolute values
    groups = {}
    for arr in arrays:
        # Extract unique absolute values, sort them to form the group key
        key = tuple(sorted({abs(x) for x in arr}))
        if key not in groups:
            groups[key] = []
        groups[key].append(arr)
    
    # Step 2: Sort groups by the length of their keys (ascending) and then by the key elements
    sorted_groups = sorted(groups.items(), key=lambda x: (len(x[0]), x[0]))
    
    # Initialize variables and unsatisfiable flag
    variables = {}
    unsatisfiable = 0
    
    for (group_key, group_arrays) in sorted_groups:
        if unsatisfiable:
            break
        
        n = len(group_key)
        group_size = len(group_arrays)
        threshold = 2 ** n
        
        # Check if group size >= 2^n
        if group_size >= threshold:
            unsatisfiable = 1
            break
        
        # Calculate 2^(n)/2 = 2^(n-1)
        count_threshold = 2 ** (n - 1)
        
        # Count positive and negative occurrences for each variable in the group
        pos_counts = {var: 0 for var in group_key}
        neg_counts = {var: 0 for var in group_key}
        
        for arr in group_arrays:
            present_vars = set()
            for num in arr:
                var = abs(num)
                if var in group_key and var not in present_vars:  # Consider each var once per array
                    present_vars.add(var)
                    if num > 0:
                        pos_counts[var] += 1
                    else:
                        neg_counts[var] += 1
        
        # Determine required changes for variables in this group
        changes = {}
        for var in group_key:
            current = variables.get(var, {0, 1})
            pos = pos_counts[var]
            neg = neg_counts[var]
            
            # Check if already fixed
            if len(current) == 1:
                # No change needed, but ensure that existing value is compatible with any possible new setting
                # Since variable is fixed, but check if this group's processing would require a conflict
                # However, according to problem statement, only set based on counts meeting threshold
                # So if variable is already fixed, skip processing unless the threshold is met here
                # But need to check if the current counts would force a conflict
                # However, per problem description, variables are fixed in previous groups and subsequent groups must check compatibility
                # So here, we only process variables not already fixed
                continue
            
            if pos >= count_threshold:
                changes[var] = 1
            elif neg >= count_threshold:
                changes[var] = 0
        
        # Apply changes and check compatibility
        for var, val in changes.items():
            current = variables.get(var, {0, 1})
            if val not in current:
                unsatisfiable = 1
                break
            variables[var] = {val}
        
        # After applying changes, check all variables in group for compatibility
        for var in group_key:
            current = variables.get(var, {0, 1})
            if len(current) == 0:
                unsatisfiable = 1
                break
        if unsatisfiable:
            break
    
    # Prepare the result
    if unsatisfiable:
        return "This formula is unsatisfiable.", None
    else:
        # Collect all variables, including those not mentioned (default to [0,1])
        all_vars = set()
        for arr in arrays:
            for num in arr:
                all_vars.add(abs(num))
        result = {}
        for var in sorted(all_vars):
            vals = variables.get(var, {0, 1})
            if vals == {0, 1}:
                result[f"x{var}"] = [0, 1]
            else:
                result[f"x{var}"] = list(vals)
        return "This formula is satisfiable, as long as there exists at least one assignment.", result

# Example usage
input_arrays = [
    [1,2],
    [1,-2],
    [-1,2],
    [-1,-2]
]

message, assignments = process_formula(input_arrays)
print(message)
if assignments is not None:
    for var in sorted(assignments.keys(), key=lambda x: int(x[1:])):
        print(f"{var} -> {assignments[var]}")
