from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTextEdit, QLabel, QPushButton, QListWidget,
    QFrame, QFormLayout, QTableWidget
)
from PySide6.QtCore import Qt, QPoint
import sys

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
        self.table = None
        self.clear_layout(self.input_layout)
        if self.current_tool is None:
            return
        input_form = self.current_tool.input_form()

        columns = input_form.get("input_table")

        # ---- Create table ----
        self.table = QTableWidget(input_form.get("default_rows", 1), len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(120)

        self.input_layout.addRow(self.table)

        # ---- Buttons ----

        run_btn = QPushButton("Run")
        run_btn.clicked.connect(self.run_current_tool)

        help_btn = QPushButton("Help")
        help_btn.clicked.connect(self.display_help)

        btn_row = QWidget()
        btn_layout = QHBoxLayout(btn_row)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        if not input_form.get("fixed_rows", False):
            add_row_btn = QPushButton("+ Add row")
            add_row_btn.clicked.connect(self.add_row)
            btn_layout.addWidget(add_row_btn)
        if not input_form.get("fixed_columns", False):
            add_column_btn = QPushButton("+ Add column")
            add_column_btn.clicked.connect(self.add_column)
            btn_layout.addWidget(add_column_btn)
        
        btn_layout.addStretch()
        btn_layout.addWidget(help_btn)
        btn_layout.addWidget(run_btn)

        self.input_layout.addRow(btn_row)

    # ----------------- Output -----------------
    def run_current_tool(self):
        for part in [self.current_tool, self.table]:
            if part is None:
                return
        
        table_data = []

        for r in range(self.table.rowCount()): # type: ignore
            row_data = {}
            has_data = False

            for c in range(self.table.columnCount()): # type: ignore
                header = self.table.horizontalHeaderItem(c).text() # type: ignore
                item = self.table.item(r, c) # type: ignore

                if item is not None and item.text().strip():
                    try:
                        row_data[header] = float(item.text())
                        has_data = True
                    except ValueError:
                        self.show_text(f"Invalid number at  r: {r+1}, c: {c+1}")
                        return
                else:
                    self.show_text(f"Invalid number at row r: {r+1}, c: {c+1}")
                    return

            if has_data:
                table_data.append(row_data)

        if not table_data:
            self.show_text("No input entered")
            return
        
        widget = self.current_tool.run(table_data) # type: ignore
        self.clear_output()
        self.output_layout.addWidget(widget)

    def display_help(self):
        if self.current_tool is None:
            return
        text = self.current_tool.help()
        self.show_text(text)

    def clear_output(self):
        while self.output_layout.count():
            item = self.output_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
    
    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def add_row(self):
        row = self.table.rowCount() # type: ignore
        self.table.insertRow(row) # type: ignore
    
    def add_column(self):
        column = self.table.columnCount() # type: ignore
        self.table.insertColumn(column) # type: ignore

    def show_text(self, text):
        self.clear_output()
        widget = QTextEdit()
        widget.setReadOnly(True)
        widget.setText(text)
        self.output_layout.addWidget(widget)


# ---------------- Entry Point ----------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())