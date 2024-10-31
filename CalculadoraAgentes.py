import tkinter as tk
from mesa import Agent, Model
from mesa.time import BaseScheduler
from collections import deque
import re

class OperationAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.result = None

    def handle(self, operands):
        pass

class SumAgent(OperationAgent):
    def handle(self, operands):
        self.result = operands[0] + operands[1]
        return self.result

class SubtractAgent(OperationAgent):
    def handle(self, operands):
        self.result = operands[0] - operands[1]
        return self.result

class MultiplyAgent(OperationAgent):
    def handle(self, operands):
        self.result = operands[0] * operands[1]
        return self.result

class DivideAgent(OperationAgent):
    def handle(self, operands):
        if operands[1] != 0:
            self.result = operands[0] / operands[1]
        else:
            self.result = "Error: División por cero"
        return self.result

class PowerAgent(OperationAgent):
    def handle(self, operands):
        self.result = operands[0] ** operands[1]
        return self.result

class InputOutputAgent(Agent):
    def __init__(self, unique_id, model, result_var):
        super().__init__(unique_id, model)
        self.queue = deque()
        self.result_var = result_var

    def step(self):
        if self.queue:
            expression = self.queue.popleft()
            result = self.evaluate_expression(expression)
            self.result_var.set(f"Resultado: {result}")

    def shunting_yard(self, expression):
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
        output_queue = []
        operator_stack = []

        for token in expression:
            if isinstance(token, (int, float)):
                output_queue.append(token)
            elif token in precedence:
                while (operator_stack and operator_stack[-1] != '(' and
                       precedence.get(token, 0) <= precedence.get(operator_stack[-1], 0)):
                    output_queue.append(operator_stack.pop())
                operator_stack.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output_queue.append(operator_stack.pop())
                if operator_stack:
                    operator_stack.pop()

        while operator_stack:
            output_queue.append(operator_stack.pop())

        return output_queue

    def evaluate_postfix(self, postfix):
        stack = []
        
        for token in postfix:
            if isinstance(token, (int, float)):
                stack.append(token)
            else:
                if len(stack) < 2:
                    return "Error: Expresión inválida"
                
                b = stack.pop()
                a = stack.pop()
                if token == '+':
                    result = self.model.sum_agent.handle([a, b])
                elif token == '-':
                    result = self.model.subtract_agent.handle([a, b])
                elif token == '*':
                    result = self.model.multiply_agent.handle([a, b])
                elif token == '/':
                    result = self.model.divide_agent.handle([a, b])
                elif token == '^':
                    result = self.model.power_agent.handle([a, b])
                stack.append(result)

        return stack[0] if stack else "Error: Expresión inválida"

    def evaluate_expression(self, expression):
        postfix = self.shunting_yard(expression)
        if not postfix:
            return "Error: Expresión vacía o inválida"
        result = self.evaluate_postfix(postfix)
        return result

    def receive_expression(self, expression):
        self.queue.append(expression)

class CalculatorModel(Model):
    def __init__(self, result_var):
        self.schedule = BaseScheduler(self)
        self.sum_agent = SumAgent(1, self)
        self.subtract_agent = SubtractAgent(2, self)
        self.multiply_agent = MultiplyAgent(3, self)
        self.divide_agent = DivideAgent(4, self)
        self.power_agent = PowerAgent(5, self)
        self.io_agent = InputOutputAgent(6, self, result_var)

        for agent in [self.sum_agent,
                      self.subtract_agent,
                      self.multiply_agent,
                      self.divide_agent,
                      self.power_agent,
                      self.io_agent]:
            self.schedule.add(agent)

    def step(self):
        self.schedule.step()

class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora Basada en Agentes")
        
        tk.Label(root, text="Ingrese la expresión matemática (Ej: 2+3*4-5):").pack()
        
        self.expression_entry = tk.Entry(root, width=30)
        self.expression_entry.pack()
        
        self.result_var = tk.StringVar()
        self.result_label = tk.Label(root, textvariable=self.result_var)
        self.result_label.pack()
        
        self.model = CalculatorModel(self.result_var)

        self.calculate_button = tk.Button(root, text="Calcular", command=self.calculate)
        self.calculate_button.pack()

    def calculate(self):
        expression_str = re.findall(r'\d+\.?\d*|[-+*/^()]', self.expression_entry.get())
        
        parsed_expression = []
        
        for token in expression_str:
            try:
                parsed_expression.append(int(token))
            except ValueError:
                try:
                    parsed_expression.append(float(token))
                except ValueError:
                    parsed_expression.append(token)

        
        if parsed_expression:
            self.model.io_agent.receive_expression(parsed_expression)
            for _ in range(len(parsed_expression)):
                self.model.step()

if __name__ == '__main__':
    root = tk.Tk()
    app = CalculatorApp(root)

    root.mainloop()
