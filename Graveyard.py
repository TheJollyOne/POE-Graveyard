from PyQt5.QtWidgets import QApplication, QTableWidget, QComboBox, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtWidgets import QListView, QCompleter
from PyQt5.QtCore import Qt, QSize
import sys
import json
from icecream import ic


class TableWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.table = QTableWidget(8, 17)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)

        self.calculate_button = QPushButton('Calculate')
        self.calculate_button.clicked.connect(self.calculate)
        layout.addWidget(self.calculate_button)

        with open('mods.json', 'r') as f:
            self.mods = json.load(f)

        for i in range(8):  # Для каждого ряда
            for j in range(17):  # Для каждой колонки
                combo = QComboBox()
                combo.setEditable(True)
                combo.view().setMinimumWidth(500)  # Устанавливаем минимальную ширину выпадающего списка
                # Устанавливаем фон выпадающего списка в белый
                combo.view().setStyleSheet("QAbstractItemView {"
                                           "background-color: white; }")
                combo.addItem("")  # Добавляем пустой элемент
                for mod in self.mods:
                    combo.addItem(mod['name'])

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
                    # Создаем QCompleter с элементами из списка mods
                    completer = QCompleter([mod['name'] for mod in self.mods], combo)

                    # Создаем QListView и устанавливаем его ширину
                    popup = QListView()
                    popup.setMinimumWidth(500)

                    # Устанавливаем QListView в качестве выпадающего списка для QCompleter
                    completer.setPopup(popup)

                    # Устанавливаем чувствительность к регистру для QCompleter
                    completer.setCaseSensitivity(Qt.CaseInsensitive)
                    # Устанавливаем режим фильтрации для QCompleter
                    completer.setFilterMode(Qt.MatchContains)

                    # Устанавливаем QCompleter для QComboBox
                    combo.setCompleter(completer)

                    for mod in self.mods:
                        if (i == 0 and j == 1) or (i == 1 and j in [2, 15]) or (i == 2 and j in [4, 14]) or \
                            (i == 4 and j in [0, 2, 6, 12]) or (i == 5 and j == 1) or \
                                (i == 6 and j in [0, 2, 7, 10, 16]):  # Условия для голубого цвета
                            adj_style = "background-color: blue"
                            if combo.styleSheet() != adj_style:
                                combo.setStyleSheet(adj_style)  # Устанавливаем фон в голубой
                        elif (i == 1 and j == 10) or (i == 3 and j == 1) or (i == 5 and j == 8) or \
                                (i == 6 and j == 12) or (i == 7 and j in [5, 14]):  # Условия для фиолетового цвета
                            row_style = "background-color: purple"
                            if combo.styleSheet() != row_style:
                                combo.setStyleSheet(row_style)  # Устанавливаем фон в фиолетовый
                        elif (i == 2 and j == 11) or (i == 3 and j == 15):  # Условия для зеленого цвета
                            col_style = "background-color: green"
                            if combo.styleSheet() != col_style:
                                combo.setStyleSheet(col_style)  # Устанавливаем фон в зеленый
                        else:
                            else_style = "background-color: white"
                            if combo.styleSheet() != else_style:
                                combo.setStyleSheet(else_style)  # Устанавливаем фон в белый
                else:
                    none_style = "background-color: black"
                    if combo.styleSheet() != none_style:
                        combo.setStyleSheet(none_style)  # Устанавливаем фон в черный
                    combo.setEnabled(False)  # Отключаем ячейку

                self.table.setCellWidget(i, j, combo)

        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, 100)  # Устанавливаем ширину колонок

        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 60)  # Устанавливаем высоту строк

        # Устанавливаем размер окна, чтобы соответствовать размеру таблицы
        self.resize(self.table.horizontalHeader().length() + 25, self.table.verticalHeader().length() + 60)

        # Ограничиваем максимальный размер окна
        self.setMaximumSize(QSize(1920, 1080))  # Замените эти значения на желаемый максимальный размер


    def calculate(self):
        totals = {}
        row_values = {}  # New variable to store row values
        row_modifiers = {}  # New variable to store row modifiers
        black_cells = {}  # New variable to store black cells
        cell_multipliers = {}
        # New variable to store column modifiers
        column_modifiers = {}
        # New variable to store black cells in columns
        black_cells_column = {}

        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                combo = self.table.cellWidget(i, j)
                if combo:
                    name = combo.currentText()
                    if name and combo.isEnabled():
                        for mod in self.mods:
                            if mod['name'] == name:
                                value = mod['value'] if 'value' in mod else 0
                                multiplier = 0  # New variable to store the multiplier

                                # Inside the loop where you process each cell
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

                    if not combo.isEnabled():  # Check if the cell is disabled (black)
                        if i not in black_cells:
                            black_cells[i] = []
                        black_cells[i].append(j)

        # Apply row modifiers
        for i in range(self.table.rowCount()):
            black_cell_indices = sorted(black_cells.get(i, []))
            row_modifier_intervals = sorted(row_modifiers.get(i, []), key=lambda x: x['start'])
            for start, end in zip([0] + black_cell_indices, black_cell_indices + [self.table.columnCount()]):
                for cell_index in range(start, end):
                    if cell_index in black_cell_indices:  # Skip if the cell is disabled (black)
                        continue
                    for interval in row_modifier_intervals:
                        if start <= interval['start'] < end:
                            # Add the row modifier's value to the multiplier for the current cell
                            if (i, cell_index) not in cell_multipliers:
                                cell_multipliers[(i, cell_index)] = []
                            cell_multipliers[(i, cell_index)].append({'source': f"Row modifier at ({i}, {interval['start']})", 'value': interval['value']})
                            break
                    else:
                        if (i, cell_index) not in cell_multipliers:
                            cell_multipliers[(i, cell_index)] = []
                        cell_multipliers[(i, cell_index)].append({'source': 'No row modifier', 'value': 1})

        # Check for column modifiers and black cells in columns
        for j in range(self.table.columnCount()):
            for i in range(self.table.rowCount()):
                combo = self.table.cellWidget(i, j)
                if combo:
                    name = combo.currentText()
                    if name and combo.isEnabled():
                        for mod in self.mods:
                            if mod['name'] == name:
                                if 'Column' in mod['type']:
                                    if j not in column_modifiers:
                                        column_modifiers[j] = []
                                    column_modifiers[j].append({'start': i, 'value': mod['value'] / 100})
                if not combo.isEnabled():  # Check if the cell is disabled (black)
                    if j not in black_cells_column:
                        black_cells_column[j] = []
                    black_cells_column[j].append(i)

        # Apply column modifiers
        for j in range(self.table.columnCount()):
            black_cell_indices = sorted(black_cells_column.get(j, []))
            column_modifier_intervals = sorted(column_modifiers.get(j, []), key=lambda x: x['start'])
            for start, end in zip([0] + black_cell_indices, black_cell_indices + [self.table.rowCount()]):
                for cell_index in range(start, end):
                    if cell_index in black_cell_indices:  # Skip if the cell is disabled (black)
                        continue
                    for interval in column_modifier_intervals:
                        if start <= interval['start'] < end:
                            # Add the column modifier's value to the multiplier for the current cell
                            if (cell_index, j) not in cell_multipliers:
                                cell_multipliers[(cell_index, j)] = []
                            cell_multipliers[(cell_index, j)].append({'source': f"Column modifier at ({interval['start']}, {j})", 'value': interval['value']})
                            break
                    else:
                        if (cell_index, j) not in cell_multipliers:
                            cell_multipliers[(cell_index, j)] = []
                        cell_multipliers[(cell_index, j)].append({'source': 'No column modifier', 'value': 1})

        # Check for adjacent cells
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                combo = self.table.cellWidget(i, j)
                if combo and combo.isEnabled():
                    for mod in self.mods:
                        if mod['name'] == combo.currentText() and 'adjacent' in mod['type']:
                            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                adj_i, adj_j = i + dx, j + dy
                                if 0 <= adj_i < self.table.rowCount() and 0 <= adj_j < self.table.columnCount() and (adj_i, adj_j) not in black_cells:
                                    if 'value' in mod:
                                        value = mod['value'] / 100  # Divide by 100 here
                                    else:
                                        value = 0
                                    if (adj_i, adj_j) not in cell_multipliers:
                                        cell_multipliers[(adj_i, adj_j)] = []
                                    cell_multipliers[(adj_i, adj_j)].append({'source': f"Adjacent cell at ({i}, {j})", 'value': value})
        # Update cell values with multipliers
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                if (i, j) in cell_multipliers:
                    if i in row_values:  # Check if the key exists in the dictionary
                        for cell_value in row_values[i]:
                            if cell_value['start'] == j:
                                cell_value['multiplier'] = 1  # Initialize multiplier as 1
                                cell_value['multiplier'] += sum(m['value'] for m in cell_multipliers[(i, j)] if m['value'] != 1)  # Exclude multipliers equal to 1

        # Display final multipliers for each cell
        multiplied_cells = {}
        non_multiplied_cells = {}
        for cell, multipliers in cell_multipliers.items():
            if cell in black_cells or cell in black_cells_column:  # Skip if the cell is disabled (black)
                continue
            if any(m['value'] != 1 for m in multipliers):
                multiplied_cells[cell] = multipliers
            else:
                non_multiplied_cells[cell] = multipliers

        # Apply multipliers to cell values and calculate totals
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                if (i, j) in cell_multipliers and i in row_values:
                    for cell_value in row_values[i]:
                        if cell_value['start'] == j:
                            # Check if the multiplier is from the same row or column and skip if it is
                            if not any(m['source'] == f"Row modifier at ({i}, {cell_value['start']})" or m['source'] == f"Column modifier at ({cell_value['start']}, {j})" for m in cell_multipliers[(i, j)]):
                                cell_value['value'] *= cell_value['multiplier']  # Apply the multiplier to the cell value
                            if cell_value['type'] not in totals:
                                totals[cell_value['type']] = 0
                            totals[cell_value['type']] += cell_value['value']  # Add the cell value to the total for its type

        # Display totals
        message = "\n".join(f"{type}: {total}" for type, total in totals.items())
        QMessageBox.information(self, "Totals", message)


app = QApplication(sys.argv)
window = TableWidget()
window.show()
sys.exit(app.exec_())
