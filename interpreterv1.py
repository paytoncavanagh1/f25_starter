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
        self.run_func(main_func_node)

    def run_func(self, func_node):
        for statement_node in func_node.get("statements"):
            self.run_statement(statement_node)

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
        val = self.expression_evaluater(expression)
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
            op2 = expression.get("op2")

            first_op = self.expression_evaluater(op1)
            second_op = self.expression_evaluater(op2)

            if not (isinstance(first_op, int) and isinstance(second_op, int)):
                super().error(
                    ErrorType.TYPE_ERROR,
                    "Incompatible types for arithmetic operation",
                )
            else:
                return first_op + second_op

        elif expression.elem_type == "-":
            op1 = expression.get("op1")
            op2 = expression.get("op2")

            first_op = self.expression_evaluater(op1)
            second_op = self.expression_evaluater(op2)

            if not (isinstance(first_op, int) and isinstance(second_op, int)):
                super().error(
                    ErrorType.TYPE_ERROR,
                    "Incompatible types for arithmetic operation",
                )
            else:
                return first_op - second_op

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
                        final_str += str(self.variable_name_to_value[var_name])
                    else:
                        super().error(
                            ErrorType.NAME_ERROR,
                            f"Variable {var_name} has not been defined",
                        )
                else:
                    val = self.expression_evaluater(arg)
                    final_str += str(val)
                    
            self.output(final_str)
        elif statement_node.get("name") == "inputi":
            arg_list = statement_node.get("args")
            
            # for arg in arg_list:
            if len(arg_list) == 0:
                return int(self.get_input())
            elif len(arg_list) == 1:
                val = self.expression_evaluater(arg_list[0])
                # final_str += str(val)
                self.output(str(val))
                return int(self.get_input())
            else:
                super().error(
                    ErrorType.NAME_ERROR,
                    f"No inputi() function found that takes > 1 parameter",
                )
        else:
            random_func = statement_node.get("name")
            super().error(
                ErrorType.NAME_ERROR,
                f"Function {random_func} has not been defined",
            )
