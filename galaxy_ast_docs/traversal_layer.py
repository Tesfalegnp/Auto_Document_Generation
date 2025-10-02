# galaxy_ast_docs/traversal_layer.py
from .language_layer import is_metta_language

def extract_definitions(tree, code_bytes, lang_name):
    """
    Extracts structured data for different languages:
    - Standard languages: Classes, functions, variables
    - MeTTa: Functions, expressions, atoms, variables, atomespaces
    """
    root_node = tree.root_node
    
    # Handle MeTTa language with custom extraction
    if is_metta_language(lang_name):
        return extract_metta_definitions(tree, code_bytes)
    
    # Handle standard languages (existing code unchanged)
    classes = []
    functions_outside = []

    def node_text(node):
        """Extract text content from node"""
        return code_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")

    def collect_variables(func_node):
        """Collect variable names inside a function node."""
        vars_found = []

        def walk_var(n):
            if lang_name == "python" and n.type == "assignment":
                if n.child_count >= 1:
                    vars_found.append(node_text(n.children[0]))
            elif lang_name in ["javascript", "typescript"] and n.type == "variable_declarator":
                name_node = n.child_by_field_name("name")
                if name_node:
                    vars_found.append(node_text(name_node))
            elif lang_name == "java" and n.type == "variable_declarator":
                name_node = n.child_by_field_name("name")
                if name_node:
                    vars_found.append(node_text(name_node))
            for c in n.children:
                walk_var(c)

        walk_var(func_node)
        return vars_found

    def walk(node, current_class=None):
        # Classes
        if lang_name == "python" and node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                current_class = {
                    "type": "class",
                    "name": node_text(name_node),
                    "line": node.start_point[0] + 1,
                    "functions": []
                }
                classes.append(current_class)

        elif lang_name in ["javascript", "typescript"] and node.type in ("class_declaration", "class_definition"):
            name_node = node.child_by_field_name("name")
            if name_node:
                current_class = {
                    "type": "class",
                    "name": node_text(name_node),
                    "line": node.start_point[0] + 1,
                    "functions": []
                }
                classes.append(current_class)

        elif lang_name == "java" and node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                current_class = {
                    "type": "class",
                    "name": node_text(name_node),
                    "line": node.start_point[0] + 1,
                    "functions": []
                }
                classes.append(current_class)

        # Functions
        if lang_name == "python" and node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                func_info = {
                    "name": node_text(name_node),
                    "line": node.start_point[0] + 1,
                    "variables": collect_variables(node),
                    "num_lines": node.end_point[0] - node.start_point[0] + 1
                }
                if current_class:
                    current_class["functions"].append(func_info)
                else:
                    functions_outside.append(func_info)

        elif lang_name in ["javascript", "typescript"] and node.type in ("function_declaration", "method_definition"):
            name_node = node.child_by_field_name("name")
            if name_node:
                func_info = {
                    "name": node_text(name_node),
                    "line": node.start_point[0] + 1,
                    "variables": collect_variables(node),
                    "num_lines": node.end_point[0] - node.start_point[0] + 1
                }
                if current_class:
                    current_class["functions"].append(func_info)
                else:
                    functions_outside.append(func_info)

        elif lang_name == "java" and node.type in ("method_declaration", "constructor_declaration"):
            name_node = node.child_by_field_name("name")
            if name_node:
                func_info = {
                    "name": node_text(name_name),
                    "line": node.start_point[0] + 1,
                    "variables": collect_variables(node),
                    "num_lines": node.end_point[0] - node.start_point[0] + 1
                }
                if current_class:
                    current_class["functions"].append(func_info)
                else:
                    functions_outside.append(func_info)

        for child in node.children:
            walk(child, current_class)

    walk(root_node)
    return {"classes": classes, "functions": functions_outside}

def extract_metta_definitions(tree, code_bytes):
    """
    Extract MeTTa definitions with proper syntax understanding:
    - Function definitions: (= (func_name params) body)
    - Expressions: (operator args...)
    - Executions: !(expression)
    - Variables: $variable (properly classified)
    - Atomespaces: &atomespace (properly classified)
    """
    root_node = tree.root_node
    
    # Containers for different MeTTa constructs
    functions = []
    expressions = []
    executions = []
    facts = []  # Simple facts like (Bob parent Alex)
    
    # Collect unique variables and atomespaces across the file
    all_variables = set()
    all_atomespaces = set()

    def collect_variables_and_atomespaces(node):
        """Recursively collect all variables and atomespaces"""
        if node.type == "variable":
            all_variables.add(node.value)
        elif node.type == "atomespace":
            all_atomespaces.add(node.value)
            
        for child in node.children:
            collect_variables_and_atomespaces(child)

    def get_expression_signature(node):
        """Get a readable signature for an expression"""
        if not node.children:
            return node.value or "empty"
            
        # Get the operator/function name (first child)
        first_child = node.children[0]
        operator = first_child.value if first_child else "unknown"
        
        # Count arguments
        arg_count = len(node.children) - 1
        
        return f"{operator}({arg_count} args)" if arg_count > 0 else operator

    def extract_function_info(node):
        """Extract information from function definition"""
        if not node.children:
            return None
            
        # Find function signature
        signature_node = None
        for child in node.children:
            if child.type == "function_signature":
                signature_node = child
                break
                
        if not signature_node:
            return None
            
        func_name = signature_node.value
        
        # Count parameters (variables in signature)
        params = []
        for child in signature_node.children:
            if child.type == "variable":
                params.append(child.value)
                
        return {
            "name": func_name,
            "Start_line": node.line,
            "end_line": node.end_line,
            "parameters_Name": params,
            "param_count": len(params)
        }

    def walk_metta_ast(node):
        """Walk MeTTa AST and categorize constructs"""
        
        # Function definitions: (= (function_name params) body)
        if node.type == "function_definition":
            func_info = extract_function_info(node)
            if func_info:
                functions.append(func_info)
                
        # Execution statements: !(expression)
        elif node.type == "execution":
            if node.children:
                executed_expr = node.children[0]
                executions.append({
                    "line": node.line,
                    "expression": get_expression_signature(executed_expr)
                })
                
        # Regular expressions and facts (Man is Mortal)
        elif node.type == "expression":
            signature = get_expression_signature(node)
            
            # Classify as fact or expression based on pattern
            if node.children and len(node.children) == 3:
                # Potential fact pattern: (Subject Predicate Object)
                first = node.children[0]
                if first.type == "atom":  # Starts with atom, likely a fact
                    facts.append({
                        "line": node.line,
                        "pattern": signature,
                        "subject": first.value
                    })
                else:
                    expressions.append({
                        "line": node.line,
                        "signature": signature
                    })
            else:
                expressions.append({
                    "line": node.line,
                    "signature": signature
                })

        # Recursively process children
        for child in node.children:
            walk_metta_ast(child)

    # First pass: collect all variables and atomespaces
    collect_variables_and_atomespaces(root_node)
    
    # Second pass: extract constructs
    walk_metta_ast(root_node)
    
    # Return concise, organized results
    return {
        "functions": functions,
        # "expressions": expressions,
        "executions": executions,
        "facts": facts,
        "variables": sorted(list(all_variables)),
        "atomespaces": sorted(list(all_atomespaces)),
        "summary": {
            "function_count": len(functions),
            "expression_count": len(expressions),
            "execution_count": len(executions),
            "fact_count": len(facts),
            "variable_count": len(all_variables),
            "atomespace_count": len(all_atomespaces)
        }
    }
