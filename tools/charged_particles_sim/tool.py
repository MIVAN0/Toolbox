import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from .script import compute_fields



class Tool:
    name = "Charged Particles (Static Forces)"

    def input_table(self):
        return ["x", "y", "q"]

    def fixed_rows(self):
        return False
    
    def fixed_columns(self):
        return True

    def run(self, params):
        particles = params
        forces = compute_fields(particles)
        return self.build_plot(particles, forces)
    

    def build_plot(self, particles, fields):
        fig = Figure()
        ax = fig.add_subplot(111)

        x = [p["x"] for p in particles]
        y = [p["y"] for p in particles]
        q = [p["q"] for p in particles]

        Ex = [f[0] for f in fields]
        Ey = [f[1] for f in fields]

        colors = ["red" if qi > 0 else "blue" for qi in q]

        ax.scatter(x, y, c=colors, zorder=3)
        ax.margins(0.25)
        ax.quiver(x, y, Ex, Ey, angles="xy")

        ax.set_aspect("equal")
        ax.grid(True)

        canvas = FigureCanvasQTAgg(fig)
        toolbar = NavigationToolbar2QT(canvas)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)

        return widget
