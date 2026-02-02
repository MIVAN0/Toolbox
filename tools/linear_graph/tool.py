from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.figure import Figure
from .script import linear_function

class Tool:
    name = "Linear Graph"
    
    def input_form(self):
        return {
            "input_table": ["a", "b"],
            "fixed_rows": True,
            "fixed_columns": True
        }

    def help(self):
        text = """Inputs:
    f(x) = a*x + b"""
        return text

    def run(self, params):
        a, b = params[0]["a"], params[0]["b"]
        x = list(range(-10, 11))
        y = linear_function(a, b, x)
        return self.build_plot(x, y)


    def build_plot(self, x, y):
        fig = Figure()
        ax = fig.add_subplot(111)
        ax.plot(x, y)
        ax.grid()
        ax.set_xlabel("x")
        ax.set_ylabel("y")

        canvas = FigureCanvasQTAgg(fig)
        toolbar = NavigationToolbar2QT(canvas)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)

        return widget
