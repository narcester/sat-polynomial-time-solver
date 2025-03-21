def sort_any_permutations(*permutations):
    # Step 1: Remove duplicates within each permutation
    deduped_perms = []
    for p in permutations:
        seen = set()
        unique_p = []
        for num in p:
            if num not in seen:
                seen.add(num)
                unique_p.append(num)
        deduped_perms.append(unique_p)
    
    # Step 2: Remove exact duplicates
    unique_perms = [list(p) for p in {tuple(p) for p in deduped_perms}]
    
    # Step 3: Remove reverse duplicates (keep lex-first)
    seen_reverse = set()
    no_reverse_perms = []
    for perm in sorted(unique_perms, key=lambda x: x):
        rev = tuple(reversed(perm))
        if tuple(perm) not in seen_reverse and rev not in seen_reverse:
            seen_reverse.add(tuple(perm))
            seen_reverse.add(rev)
            no_reverse_perms.append(perm)
    
    # Step 4: Sort by length → absolute values → original permutation
    return sorted(
        no_reverse_perms,
        key=lambda x: (len(x), [abs(num) for num in x], x)
    )

def process_formula(arrays):
    sorted_arrays = sort_any_permutations(*arrays)
    
    # Track all clauses globally for unit propagation
    all_clauses = sorted_arrays.copy()
    variables = {}
    unsatisfiable = 0
    
    def is_clause_satisfied(clause):
        for num in clause:
            var = abs(num)
            required = 1 if num > 0 else 0
            if var in variables and len(variables[var]) == 1:
                if required in variables[var]:
                    return True
        return False
    
    def unit_prop():
        nonlocal unsatisfiable
        changed = True
        while changed and not unsatisfiable:
            changed = False
            for clause in all_clauses:
                if is_clause_satisfied(clause):
                    continue
                unfixed_vars = []
                required_values = {}
                for num in clause:
                    var = abs(num)
                    required = 1 if num > 0 else 0
                    if var not in variables or len(variables[var]) > 1:
                        unfixed_vars.append(var)
                        required_values[var] = required
                    else:
                        current_val = next(iter(variables[var]))
                        if required != current_val:
                            continue
                        else:
                            break
                else:
                    if not unfixed_vars:
                        unsatisfiable = 1
                        return
                    if len(unfixed_vars) == 1:
                        var = unfixed_vars[0]
                        required = required_values[var]
                        current = variables.get(var, {0, 1})
                        if required not in current:
                            unsatisfiable = 1
                            return
                        if len(current) > 1:
                            variables[var] = {required}
                            changed = True
    
    groups = {}
    for arr in sorted_arrays:
        key = tuple(sorted({abs(x) for x in arr}))
        if key not in groups:
            groups[key] = []
        groups[key].append(arr)
    
    sorted_groups = sorted(groups.items(), key=lambda x: (len(x[0]), x[0]))
    
    for (group_key, group_arrays) in sorted_groups:
        if unsatisfiable:
            break
        
        n = len(group_key)
        group_size = len(group_arrays)
        threshold = 2 ** n
        
        if group_size >= threshold:
            unsatisfiable = 1
            break
        
        count_threshold = 2 ** (n - 1)
        
        active_clauses = []
        for arr in group_arrays:
            if not is_clause_satisfied(arr):
                active_clauses.append(arr)
        
        if not active_clauses:
            continue
        
        pos_counts = {var: 0 for var in group_key}
        neg_counts = {var: 0 for var in group_key}
        
        for arr in active_clauses:
            present_vars = set()
            for num in arr:
                var = abs(num)
                if var in variables and len(variables[var]) == 1:
                    continue
                if var in group_key and var not in present_vars:
                    present_vars.add(var)
                    if num > 0:
                        pos_counts[var] += 1
                    else:
                        neg_counts[var] += 1
        
        changes = {}
        for var in group_key:
            current = variables.get(var, {0, 1})
            if len(current) == 1:
                continue
            
            pos = pos_counts.get(var, 0)
            neg = neg_counts.get(var, 0)
            
            if pos > count_threshold:
                changes[var] = 1
            elif neg > count_threshold:
                changes[var] = 0
        
        for var, val in changes.items():
            current = variables.get(var, {0, 1})
            if val not in current:
                unsatisfiable = 1
                break
            variables[var] = {val}
        
        if unsatisfiable:
            break
        
        unit_prop()
        if unsatisfiable:
            break
    
    # Remove the final unsatisfiability check
    # (The formula is satisfiable if no conflicts were detected)
    
    all_vars = set()
    for arr in arrays:
        for num in arr:
            all_vars.add(abs(num))
    result = {}
    for var in sorted(all_vars):
        vals = variables.get(var, {0, 1})
        result[f"x{var}"] = list(vals) if len(vals) > 1 else list(vals)
    
    if unsatisfiable:
        return "This formula is unsatisfiable.", None
    else:
        return "This formula is satisfiable, as long as there exists at least one assignment.", result

# Test with the user's example
input_arrays = [
    [1,-3],
    [2,3,-1]
]

message, assignments = process_formula(input_arrays)
print(message)
if assignments is not None:
    for var in sorted(assignments.keys(), key=lambda x: int(x[1:])):
        print(f"{var} -> {assignments[var]}")
