# =============================
# main.py  (GUI ONLY)
# =============================
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTextEdit, QLabel, QPushButton, QListWidget,
    QFrame, QLineEdit, QFormLayout
)
from PySide6.QtCore import Qt, QPropertyAnimation, QPoint
import sys

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import os, importlib


# ---------------- Slide Menu ----------------
class SlideMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background-color: #2b2b2b; color: white;")
        self.setFixedWidth(220)
        parent_height = parent.height() if parent else 700
        self.setGeometry(-190, 0, 250, parent_height)  # initially hidden offscreen
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("  Tools")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        self.tool_list = QListWidget()
        layout.addWidget(self.tool_list)


# ---------------- Main Window ----------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Python Toolbox")
        self.resize(1920, 1080)

        self.menu_visible = False
        self.menu_width = 220

        # ---- Tool registry ----
        self.tools = {}
        tools_dir = "tools"
        for folder in os.listdir(tools_dir):
            tool_path = os.path.join(tools_dir, folder, "tool.py")
            if os.path.exists(tool_path):
                module_name = f"tools.{folder}.tool"
                module = importlib.import_module(module_name)
                tool_class = getattr(module, "Tool")  # all tool classes should be named 'Tool'
                self.tools[tool_class().name] = tool_class()
        
        self.current_tool = None
        self.param_inputs = {}
        
        central = QWidget()
        self.setCentralWidget(central)
        self.root_layout = QVBoxLayout(central)
        self.root_layout.setContentsMargins(40, 10, 20, 10)

        # Splitter: Input/Output
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.root_layout.addWidget(self.splitter)

        # Input / Output Areas
        self.input_area = QFrame()
        self.input_layout = QFormLayout(self.input_area)
        self.splitter.addWidget(self.input_area)

        self.output_area = QFrame()
        self.output_layout = QVBoxLayout(self.output_area)
        self.splitter.addWidget(self.output_area)

        self.splitter.setSizes([200, 500])

        # ---- Slide menu ----
        self.menu = SlideMenu(self)
        self.menu.tool_list.itemActivated.connect(self.select_tool)
        self.menu.raise_()  # ensure overlay

        # Populate menu dynamically
        for tool_name in self.tools.keys():
            self.menu.tool_list.addItem(tool_name)

        # ---- Floating toggle button ----
        self.toggle_button = QPushButton("☰", self)
        self.toggle_button.setFixedSize(20, 20)
        self.toggle_button.move(5, 10)
        self.toggle_button.setStyleSheet("background-color: #2b2b2b; color: white; border: none; font-size: 20pt;")
        self.toggle_button.clicked.connect(self.toggle_menu)
        self.toggle_button.raise_()

        # ---- Animation ----
        from PySide6.QtCore import QPropertyAnimation, QPoint
        self.menu_anim = QPropertyAnimation(self.menu, b"pos")
        self.menu_anim.setDuration(250)

        # Default tool
        if self.tools:
            first_tool_name = list(self.tools.keys())[0]
            self.select_tool_by_name(first_tool_name)

    # ----------------- Slide menu -----------------
    def toggle_menu(self):
        end_x = 0 if not self.menu_visible else -self.menu_width + 30
        self.menu_anim.stop()
        self.menu_anim.setStartValue(self.menu.pos())
        self.menu_anim.setEndValue(QPoint(end_x, 0))
        self.menu_anim.start()
        self.menu_visible = not self.menu_visible

    # ----------------- Tool selection -----------------
    def select_tool(self, item):
        self.select_tool_by_name(item.text())

    def select_tool_by_name(self, tool_name):
        self.current_tool = self.tools.get(tool_name)
        self.build_input_form()
        self.clear_output()


    def build_input_form(self):
        if self.current_tool is None:
            return
        if self.current_tool.parameters() is None:
            return

        while self.input_layout.count():
            item = self.input_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.param_inputs.clear()

        for name, default in self.current_tool.parameters().items():
            field = QLineEdit(str(default))
            self.param_inputs[name] = field
            self.input_layout.addRow(f"{name}:", field)

        run_button = QPushButton("Run")
        run_button.clicked.connect(self.run_current_tool)
        self.input_layout.addRow(run_button)

    def run_current_tool(self):
        if self.current_tool is None:
            return
        
        try:
            params = {
                name: float(field.text())
                for name, field in self.param_inputs.items()
            }
        except ValueError:
            self.show_text_output("Invalid input")
            return

        result = self.current_tool.run(params)
        self.show_plot(result)

    # -------- Output helpers --------
    def clear_output(self):
        while self.output_layout.count():
            item = self.output_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
    
    def show_plot(self, data):
        self.clear_output()
        x, y = data

        fig = Figure()
        canvas = FigureCanvasQTAgg(fig)
        ax = fig.add_subplot(111)
        ax.plot(x, y)

        self.output_layout.addWidget(canvas)

    def show_text_output(self, text):
        self.clear_output()
        self.output_layout.addWidget(QTextEdit(text))


# ---------------- Entry Point ----------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())