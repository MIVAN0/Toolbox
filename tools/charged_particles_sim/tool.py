from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QHBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from .script import compute_fields



class Tool:
    name = "Charged Particles"

    def input_form(self):
        return {
            "input_table": ["x", "y", "q"],
            "fixed_columns": True,
            "default_rows": 2
        }

    def help(self):
        text = """Inputs:
    coordinates (x,y) in meters,
    charge (q) in coulombs, e notation is valid (1.602*10^-19 = 1.602e-19)"""
        return text

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
        
        # Creating plot widget
        canvas = FigureCanvasQTAgg(fig)
        toolbar = NavigationToolbar2QT(canvas)

        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.addWidget(toolbar)
        plot_layout.addWidget(canvas)

        # Creating text widget
        text = QTextEdit()
        text.setReadOnly(True)
        
        lines = []
        for i, p in enumerate(particles):
            lines.append(f"Q{i+1}: ({p['x']}, {p['y']}), E={Ex[i]:.6e}i + {Ey[i]:.6e}j")
        text.setText("\n".join(lines))

        # Setting plot and text side by side
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(plot_widget, 3)
        layout.addWidget(text, 1)

        return widget
