from PyQt5.QtWidgets import QApplication, QTableWidget, QLineEdit, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtWidgets import QListView, QCompleter, QTableWidgetItem, QListWidget
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtGui
import sys
import json
from functools import partial
from PyQt5.QtWidgets import QHeaderView
from collections import Counter


def focusInEvent(line_edit, completer, event, mods):
    QLineEdit.focusInEvent(line_edit, event)
    if event.reason() == Qt.MouseFocusReason:
        completer.complete()

    def on_completer_activated(completion):
        for mod in mods:
            if mod['name'] == completion:
                line_edit.setText(mod['show'])
                break

    completer.activated.connect(on_completer_activated)


class TableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('POE-Graveyard')
        self.setStyleSheet("""
            QLineEdit { background-color: #3E424B; color: #C4C3D0; }
            QLineEdit[readOnly="true"] { background-color: #808080; color: #C4C3D0; }
            QPushButton { background-color: #2f2f2f; color: #C4C3D0; }
            QPushButton:hover { background-color: #3E424B; }
            QPushButton:pressed { background-color: #6F7678; }
            QTableWidget { background-color: #2f2f2f; color: #C4C3D0; }
            QWidget { background-color: #2f2f2f; }
            QListView { background-color: #2f2f2f; color: #C4C3D0; }
            QMessageBox { background-color: #2f2f2f; color: #C4C3D0; }
            QMessageBox QLabel { background-color: #2f2f2f; color: #C4C3D0; }
        """)

        self.table = QTableWidget(8, 17)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.calculate_button = QPushButton('Calculate')
        self.calculate_button.clicked.connect(self.calculate)
        layout.addWidget(self.calculate_button)

        # Добавьте QListWidget под кнопкой "Calculate"
        self.mod_list = QListWidget()
        # self.mod_list.setFlow(QListView.LeftToRight)  # Измените направление на горизонтальное
        self.mod_list.setWrapping(True)  # Включите автоматический перенос
        self.mod_list.setFixedHeight(100)  # Установите фиксированную высоту
        layout.addWidget(self.mod_list)

        with open('mods.json', 'r') as f:
            self.mods = json.load(f)

        self.show_to_name = {mod['show']: mod['name'] for mod in self.mods}

        for i in range(8):  # Для каждого ряда
            for j in range(17):  # Для каждой колонки
                item = QTableWidgetItem()
                if not (
                    (i == 0 and 3 <= j <= 14) or
                    (i == 1 and 5 <= j <= 9) or
                    (i == 2 and (0 <= j <= 2 or 7 <= j <= 10 or j in [12, 13, 16])) or
                    (i == 3 and (7 <= j <= 10 or 12 <= j <= 13)) or
                    (i == 4 and (j == 4 or 8 <= j <= 10)) or
                    (i == 5 and (3 <= j <= 5 or 13 <= j <= 14)) or
                    (i == 6 and (4 <= j <= 5 or 13 <= j <= 14)) or
                    (i == 7 and 8 <= j <= 9)
                ):
                    line_edit = QLineEdit()
                    line_edit.setStyleSheet("""
                                            QLineEdit { background-color: #2f2f2f; color: #C4C3D0; }
                                            QListView { background-color: #2f2f2f; color: #C4C3D0; }
                                            """)
                    line_edit.textChanged.connect(self.update_mod_list)

                    line_edit.setReadOnly(False)  # разрешаем ввод текста
                    completer = QCompleter([mod['name'] for mod in self.mods], line_edit)
                    popup = QListView()
                    popup.setStyleSheet("""
                                        QListView { background-color: #2f2f2f; color: #C4C3D0; }
                                        """)
                    popup.setMinimumWidth(500)
                    completer.setPopup(popup)
                    completer.setCaseSensitivity(Qt.CaseInsensitive)
                    completer.setFilterMode(Qt.MatchContains)
                    line_edit.setCompleter(completer)
                    line_edit.focusInEvent = partial(focusInEvent, line_edit, completer, mods=self.mods)

                    for mod in self.mods:
                        if (i == 0 and j == 1) or (i == 1 and j in [2, 15]) or (i == 2 and j in [4, 14]) or \
                            (i == 4 and j in [0, 2, 6, 12]) or (i == 5 and j == 1) or \
                                (i == 6 and j in [0, 2, 7, 10, 16]):
                            adj_style = "background-color: #4D4D5C"
                            if line_edit.styleSheet() != adj_style:
                                line_edit.setStyleSheet(adj_style)
                        elif (i == 1 and j == 10) or (i == 3 and j == 1) or (i == 5 and j == 8) or \
                                (i == 6 and j == 12) or (i == 7 and j in [5, 14]):
                            row_style = "background-color: #594D58"
                            if line_edit.styleSheet() != row_style:
                                line_edit.setStyleSheet(row_style)
                        elif (i == 2 and j == 11) or (i == 3 and j == 15):
                            col_style = "background-color: #59656d"
                            if line_edit.styleSheet() != col_style:
                                line_edit.setStyleSheet(col_style)

                    self.table.setCellWidget(i, j, line_edit)
                else:
                    item.setBackground(QtGui.QColor("#151515"))
                    self.table.setItem(i, j, item)

        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, 100)

        # self.resize(self.table.horizontalHeader().length() + 25, self.table.verticalHeader().length() + 60)

        self.setMaximumSize(QSize(1920, 1080))
        self.setMinimumSize(QSize(1900, 700))

    def calculate(self):
        totals = {}
        row_values = {}  # New variable to store row values
        row_modifiers = {}  # New variable to store row modifiers
        disabled_cells = {}  # New variable to store black cells
        cell_multipliers = {}
        # New variable to store column modifiers
        column_modifiers = {}
        # New variable to store black cells in columns
        disabled_cells_column = {}
        show_to_name = {mod['show']: mod['name'] for mod in self.mods}

        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                line_edit = self.table.cellWidget(i, j)
                if line_edit is None:
                    if i not in disabled_cells:
                        disabled_cells[i] = []
                    disabled_cells[i].append(j)
                elif line_edit:
                    name = show_to_name.get(line_edit.text())
                    if name:
                        for mod in self.mods:
                            if mod['name'] == name:
                                value = mod['value'] if 'value' in mod else 0
                                multiplier = 0
                                if 'Row' in mod['type']:
                                    if i not in row_modifiers:
                                        row_modifiers[i] = []
                                    row_modifiers[i].append({'start': j, 'value': value / 100})
                                    # Save the row modifier with the cell values
                                    if i not in row_values:
                                        row_values[i] = []
                                    row_values[i].append({'start': j,
                                                          'value': value, 'multiplier': multiplier,
                                                          'type': mod['type']})
                                else:
                                    if i not in row_values:
                                        row_values[i] = []
                                    row_values[i].append({'start': j,
                                                          'value': value, 'multiplier': multiplier,
                                                          'type': mod['type']})
        # Apply row modifiers
        for i in range(self.table.rowCount()):
            black_cell_indices = sorted(disabled_cells.get(i, []))
            row_modifier_intervals = sorted(row_modifiers.get(i, []), key=lambda x: x['start'])
            for interval in row_modifier_intervals:
                start = interval['start']
                end = next((index for index in black_cell_indices if index > start), self.table.columnCount())
                # Apply the modifier to the cells to the right of the modifier
                for cell_index in range(start + 1, end):
                    # Add the row modifier's value to the multiplier for the current cell
                    if (i, cell_index) not in cell_multipliers:
                        cell_multipliers[(i, cell_index)] = []
                    cell_multipliers[(i, cell_index)].append({'source': f"Row modifier at ({i}, {start})",
                                                              'value': interval['value']})
                # Find the previous black cell
                prev_black_cell = next((index for index in reversed(black_cell_indices) if index < start), -1)
                # Apply the modifier to the cells to the left of the modifier
                for cell_index in range(start - 1, prev_black_cell, -1):
                    # Add the row modifier's value to the multiplier for the current cell
                    if (i, cell_index) not in cell_multipliers:
                        cell_multipliers[(i, cell_index)] = []
                    cell_multipliers[(i, cell_index)].append({'source': f"Row modifier at ({i}, {start})",
                                                              'value': interval['value']})

        # Check for column modifiers and black cells in columns
        for j in range(self.table.columnCount()):
            for i in range(self.table.rowCount()):
                line_edit = self.table.cellWidget(i, j)
                if line_edit:
                    name = show_to_name.get(line_edit.text())
                    if name and line_edit.isEnabled():
                        for mod in self.mods:
                            if mod['name'] == name:
                                if 'Column' in mod['type']:
                                    if j not in column_modifiers:
                                        column_modifiers[j] = []
                                    column_modifiers[j].append({'start': i, 'value': mod['value'] / 100})
                if line_edit is None:
                    if j not in disabled_cells_column:
                        disabled_cells_column[j] = []
                    disabled_cells_column[j].append(i)

        # Apply column modifiers
        for j in range(self.table.columnCount()):
            black_cell_indices = sorted(disabled_cells_column.get(j, []))
            column_modifier_intervals = sorted(column_modifiers.get(j, []), key=lambda x: x['start'])
            for interval in column_modifier_intervals:
                start = interval['start']
                end = next((index for index in black_cell_indices if index > start), self.table.rowCount())
                # Apply the modifier to the cells below the modifier
                for cell_index in range(start + 1, end):
                    # Add the column modifier's value to the multiplier for the current cell
                    if (cell_index, j) not in cell_multipliers:
                        cell_multipliers[(cell_index, j)] = []
                    cell_multipliers[(cell_index, j)].append({'source': f"Column modifier at ({start}, {j})",
                                                              'value': interval['value']})
                    # Apply the modifier to the cells above the modifier
                    for cell_index in range(start - 1, -1, -1):
                        # Add the column modifier's value to the multiplier for the current cell
                        if (cell_index, j) not in cell_multipliers:
                            cell_multipliers[(cell_index, j)] = []
                        cell_multipliers[(cell_index, j)].append({'source': f"Column modifier at ({start}, {j})",
                                                                  'value': interval['value']})

        # Check for adjacent cells
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                line_edit = self.table.cellWidget(i, j)
                if line_edit and line_edit is not None:
                    # Use the show_to_name dictionary to get the name from the show string
                    name = show_to_name.get(line_edit.text())
                    if name:
                        for mod in self.mods:
                            if mod['name'] == name and 'adjacent' in mod['type']:
                                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                    adj_i, adj_j = i + dx, j + dy
                                    if 0 <= adj_i < self.table.rowCount() and 0 <= adj_j < self.table.columnCount(

                                    ) and (adj_i, adj_j) not in disabled_cells:
                                        if 'value' in mod:
                                            value = mod['value'] / 100  # Divide by 100 here
                                        else:
                                            value = 0
                                        if (adj_i, adj_j) not in cell_multipliers:
                                            cell_multipliers[(adj_i, adj_j)] = []
                                        cell_multipliers[(adj_i, adj_j)].append(
                                            {'source': f"Adjacent cell at ({i}, {j})",
                                             'value': value})
        # Update cell values with multipliers
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                if (i, j) in cell_multipliers:
                    if i in row_values:
                        for cell_value in row_values[i]:
                            if cell_value['start'] == j:
                                cell_value['multiplier'] = 1
                                cell_value['multiplier'] += sum(
                                    m['value'] for m in cell_multipliers[(i, j)] if m['value'] != 1)

        # Display final multipliers for each cell
        multiplied_cells = {}
        non_multiplied_cells = {}
        for cell, multipliers in cell_multipliers.items():
            if cell in disabled_cells or cell in disabled_cells_column:  # Skip if the cell is disabled (black)
                continue
            if any(m['value'] != 1 for m in multipliers):
                multiplied_cells[cell] = multipliers
            else:
                non_multiplied_cells[cell] = multipliers

        # Apply multipliers to cell values and calculate totals
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                if i in row_values:
                    for cell_value in row_values[i]:
                        if cell_value['start'] == j:
                            if (i, j) in cell_multipliers:
                                # Check if the multiplier is from the same row or column and skip if it is
                                if not any(
                                    m['source'] == f"Row modifier at ({i}, {cell_value['start']})" or
                                    m['source'] == f"Column modifier at ({cell_value['start']}, {j})"
                                    for m in cell_multipliers[(i, j)]
                                ):
                                    cell_value['value'] *= cell_value['multiplier']
                            if cell_value['type'] not in totals:
                                totals[cell_value['type']] = 0
                            totals[cell_value['type']] += cell_value['value']

        message_box = QMessageBox()
        message = "\n".join(f"{type}: {total}" for type, total in totals.items())
        message_box.about(self, "Totals", message)

    def update_mod_list(self):
        # Соберите имена всех модификаторов в таблице
        mod_names = []
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                line_edit = self.table.cellWidget(i, j)
                if line_edit is not None:
                    name = self.show_to_name.get(line_edit.text())
                    if name is not None:
                        mod_names.append(name)

        # Подсчитайте количество каждого модификатора
        mod_counts = Counter(mod_names)

        # Очистите список модификаторов
        self.mod_list.clear()

        # Добавьте модификаторы в список
        for name, count in mod_counts.items():
            self.mod_list.addItem(f"{count} - {name}")


app = QApplication(sys.argv)
window = TableWidget()
window.show()
sys.exit(app.exec_())
