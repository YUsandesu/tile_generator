from math import radians
import py5

class LSystem:
    def __init__(self):
        self.steps = 0
        self.axiom = "F"
        self.rule = "F+F-F"
        self.startLength = 90.0
        self.theta = radians(120.0)

    def reset(self):
        self.production = self.axiom
        self.drawLength = self.startLength
        self.generations = 0

    def render(self):
        py5.translate(py5.width / 2, py5.height / 2)
        self.steps += 5
        if self.steps > len(self.production):
            self.steps = len(self.production)
        for i in range(self.steps):
            step = self.production[i]
            if step == 'F':
                py5.rect(0, 0, -self.drawLength, -self.drawLength)
                py5.no_fill()
                py5.translate(0, -self.drawLength)
            elif step == '+':
                py5.rotate(self.theta)
            elif step == '-':
                py5.rotate(-self.theta)
            elif step == '[':
                py5.push_matrix()
            elif step == ']':
                py5.pop_matrix()

    def simulate(self, gen):
        while self.generations < gen:
            # print(self.production)
            self.production = self.iterate(self.production, self.rule, 0.4)

    def iterate(self, prod_, rule_, factor=0.6):
        self.drawLength *= factor
        self.generations += 1
        newProduction = prod_.replace("F", rule_)
        return newProduction


class PenroseSnowflakeLSystem(LSystem):
    def __init__(self):
        super().__init__()
        self.axiom = "F3-F3-F3-F3-F"
        # self.axiom = "F3-F"
        # self.axiom = "F3-F3-F45-F++F"
        # self.axiom = "F3-F3-F45-F++F3-F3-F3-F3-F45-F++F3-F"
        # self.axiom = "F3-F3-F45-F++F3-F3-F3-F3-F45-F++F3-F3-F3-F3-F3-F45-F++F3-F"
        # self.axiom = "F3-F3-F45-F++F3-F"
        # self.ruleF = "F"
        self.ruleF = "F3-F3-F45-F++F3-F"
        self.startLength = 100.0
        self.theta = radians(18.0)
        self.reset()

    def reset(self):
        super().reset()
        self.rule = self.ruleF

    def render(self):
        py5.translate(py5.width / 2, py5.height / 2)
        repeats = 1
        self.steps += 3
        if self.steps > len(self.production):
            self.steps = len(self.production)
        for i in range(self.steps):
            step = self.production[i]
            if step == 'F':
                for _ in range(repeats):
                    py5.line(0, 0, 0, -self.drawLength)
                    py5.translate(0, -self.drawLength)
                repeats = 1
            elif step == '+':
                for _ in range(repeats):
                    py5.rotate(self.theta)
                repeats = 1
            elif step == '-':
                for _ in range(repeats):
                    py5.rotate(-self.theta)
                repeats = 1
            # elif step == '[':
            #     py5.push_matrix()
            # elif step == ']':
            #     py5.pop_matrix()
            elif 0 <= eval(step) <= 9:  # Handle repeat counts
                repeats += int(eval(step))

    # def iterate(self, prod_, rule_):
    #     newProduction = ""
    #     for step in prod_:
    #         if step == 'F':
    #             newProduction += self.ruleF
    #         else:
    #             newProduction += step
    #     self.drawLength *= 0.4
    #     self.generations += 1
    #     return newProduction


ps = None
def setup():
    global ps
    py5.size(640, 360)
    py5.stroke(255)
    py5.no_fill()
    ps = PenroseSnowflakeLSystem()
    ps.simulate(1)

def draw():
    py5.background(0)
    ps.render()

py5.run_sketch()