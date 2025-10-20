from intbase import InterpreterBase
from intbase import ErrorType
from brewparse import parse_program

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase's constructor
        self.variable_name_to_value = {}

    def get_main_func_node(self, ast):
        func_nodes = ast.get("functions")

        if func_nodes[0].get("name") == "main":
            return func_nodes[0]
        else:
            return super().error(
                ErrorType.NAME_ERROR,
                "No main() function was found",
            )

    def run(self, program):
        ast = parse_program(program)         # parse program and outputs AST
        # self.variable_name_to_value = {}  # dict to hold variables
        main_func_node = self.get_main_func_node(ast)
        print("main function node --> ", main_func_node, " <--")
        self.run_func(main_func_node)

    def run_func(self, func_node):
        for statement_node in func_node.get("statements"):
            self.run_statement(statement_node)
            print("Statement node --> ", statement_node, "\nstatement node.get --> ", statement_node.get("name"))

    def run_statement(self, statement_node):
        if self.is_definition(statement_node):
            self.do_definition(statement_node)
        elif self.is_assignment(statement_node):
            self.do_assignment(statement_node)
        elif self.is_func_call(statement_node):
            self.do_func_call(statement_node)

    def is_definition(self, statement_node):
        if statement_node.elem_type == InterpreterBase.VAR_DEF_NODE:
            return True
        else:
            return False
        
    def do_definition(self, statement_node):
        var_name = statement_node.get('name')

        # if the variable name is already in the map, then return an error
        if var_name in self.variable_name_to_value:
            return super().error(
                    ErrorType.NAME_ERROR,
                    f"Variable {var_name} defined more than once",
                    )
        else:
            self.variable_name_to_value[var_name] = None

    def is_assignment(self, statement_node):
        if statement_node.elem_type == InterpreterBase.ASSIGNMENT_NODE:
            return True
        else:
            return False
        
    def do_assignment(self, statement_node):
        expression_var = statement_node.get("var")
        # if the var we are trying to use in our expression is not in our map
        if expression_var not in self.variable_name_to_value:
            return super().error(
                ErrorType.NAME_ERROR,
                f"Variable {expression_var} has not been defined",
            )
        
        expression = statement_node.get("expression")
        val = str(self.expression_evaluater(expression))
        self.variable_name_to_value[expression_var] = val

    def expression_evaluater(self, expression):
        if self.is_variable_node(expression):
            return self.evaluate_variable_node(expression)
        elif self.is_value_node(expression):
                return self.evaluate_value_node(expression)
        elif expression.elem_type == InterpreterBase.FCALL_NODE:
            return self.do_func_call(expression)
        elif self.is_binary_operator(expression):
            return self.evaluate_binary_operator(expression)

    def is_value_node(self, expression):
        if expression.elem_type == InterpreterBase.INT_NODE or expression.elem_type == InterpreterBase.STRING_NODE:
            return True
        else:
            return False
        
    def evaluate_value_node(self, expression):
        return expression.get("val")
    
    def is_variable_node(self, expression):
        if expression.elem_type == InterpreterBase.QUALIFIED_NAME_NODE:
            return True
        else:
            return False

    def evaluate_variable_node(self, expression):
        var_name = expression.get("name")
        return self.variable_name_to_value[var_name]

    def is_binary_operator(self, expression):
        if expression.elem_type == "+" or expression.elem_type == "-":
            return True
        else:
            return False
        
    def evaluate_binary_operator(self, expression):
        if expression.elem_type == "+":
            op1 = expression.get("op1")
            if op1.elem_type != InterpreterBase.QUALIFIED_NAME_NODE:
                op1_val = int(op1.get("val"))
            else:
                op1_var = op1.get("name")
                op1_val = int(self.variable_name_to_value[op1_var])

            op2 = expression.get("op2")
            if op2.elem_type != InterpreterBase.QUALIFIED_NAME_NODE:
                op2_val = int(op2.get("val"))
            else:
                op2_var = op2.get("name")
                op2_val = int(self.variable_name_to_value[op2_var])
            
            if op1.elem_type == InterpreterBase.STRING_NODE and op2.elem_type == InterpreterBase.INT_NODE or op1.elem_type == InterpreterBase.INT_NODE and op2.elem_type == InterpreterBase.STRING_NODE:
                super().error(
                    ErrorType.TYPE_ERROR,
                    "Incompatible types for arithmetic operation",
                )
            else:
                return op1_val + op2_val

        elif expression.elem_type == "-":
            op1 = expression.get("op1")
            op1_val = op1.get("val")

            op2 = expression.get("op2")
            op2_val = op2.get("val")

            if op1.elem_type == InterpreterBase.STRING_NODE and op2.elem_type == InterpreterBase.INT_NODE or op1.elem_type == InterpreterBase.INT_NODE and op2.elem_type == InterpreterBase.STRING_NODE:
                super().error(
                    ErrorType.TYPE_ERROR,
                    "Incompatible types for arithmetic operation",
                )
            else:
                return op1_val - op2_val

    def is_func_call(self, statement_node):
        if statement_node.elem_type == InterpreterBase.FCALL_NODE:
            return True
        else:
            return False

    def do_func_call(self, statement_node):
        final_str = ""
        if statement_node.get("name") == "print":
            arg_list = statement_node.get("args")

            if not arg_list:
                return self.output("")
            
            for arg in arg_list:
                if arg.elem_type == InterpreterBase.QUALIFIED_NAME_NODE:
                    var_name = arg.get("name")
                    if var_name in self.variable_name_to_value:
                        final_str += self.variable_name_to_value[var_name]
                    else:
                        super().error(
                            ErrorType.NAME_ERROR,
                            f"Variable {var_name} has not been defined",
                        )
                else:
                    final_str += str(arg.get("val"))
                    
            self.output(final_str)

        elif statement_node.get("name") == "inputi":
            arg_list = statement_node.get("args")
            
            for arg in arg_list:
                final_str += str((arg.get("val")))
                self.output(final_str)
                return str(self.get_input())
        else:
            super().error(
                ErrorType.NAME_ERROR,
                f"Function {statement_node.get("name")} has not been defined",
            )

	# def do_assignment(self, statement_node):
	# 	target_var_name = get_target_variable_name(statement_node)
    #     if !var_name_exists(target_var_name):
    #         generate_error("Undefined variable " + target_var_name)
	# 	source_node = get_expression_node(statement_node)
	# 	resulting_value = evaluate_expression(source_node)
	# 	this.variable_name_to_value[target_var_name] = resulting_value
     
    # def evaluate_expression(self, expression_node):
    #     if is_value_node(expression_node):
    #         return get_value(expression_node)
    #     else if is_variable_node(expression_node):
    #         return get_value_of_variable(expression_node)
    #     else if is_binary_operator(expression_node):
    #         return evaluate_binary_operator(expression_node)