import os
import sys
import csv
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import numpy as np
from utils import retrieve_parity_marks

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

# Set background to white
#pg.setConfigOption('background', 'w')
#pg.setConfigOption('foreground', 'k')
#pg.setConfigOptions(antialias=True)

class PlotWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Load data
        self.time, self.flow, self.pressure, self.volume, self.pmus, self.ref = self.load_data('coletapcv_adequate.csv')
        self.ins_marks, self.exp_marks = retrieve_parity_marks(self.volume * 10)

        self.current_cycle_index = 0
        self.button_states = [{} for _ in range(len(self.ins_marks))]  # asynchrony states for each cycle

        pg_layout = pg.GraphicsLayoutWidget()

        plot_layout = QtWidgets.QVBoxLayout()
        plot_layout.addWidget(pg_layout)

        self.plot1 : pg.PlotItem = pg_layout.addPlot(row=0, col=0)
        self.plot2 : pg.PlotItem = pg_layout.addPlot(row=1, col=0)
        self.plot3 : pg.PlotItem = pg_layout.addPlot(row=2, col=0)

        self.plot1.showGrid(x=True, y=True)
        self.plot2.showGrid(x=True, y=True)
        self.plot3.showGrid(x=True, y=True)

        self.plot2.setXLink(self.plot1)
        self.plot3.setXLink(self.plot1)

        button_layout = QtWidgets.QVBoxLayout()
        self.double_trigger_button = QtWidgets.QPushButton("Double Trigger")
        self.reverse_trigger_button = QtWidgets.QPushButton("Reverse Trigger")
        self.early_cycling_button = QtWidgets.QPushButton("Early Cycling")

        self.double_trigger_button.setCheckable(True)
        self.reverse_trigger_button.setCheckable(True)
        self.early_cycling_button.setCheckable(True)

        button_layout.addWidget(self.double_trigger_button)
        button_layout.addWidget(self.reverse_trigger_button)
        button_layout.addWidget(self.early_cycling_button)
        button_layout.addStretch()  # push buttons to the top

        self.double_trigger_button.clicked.connect(self.update_button_state)
        self.reverse_trigger_button.clicked.connect(self.update_button_state)
        self.early_cycling_button.clicked.connect(self.update_button_state)

        # horizontal layout to contain both plot and button layout
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(plot_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.plot_data()
        self.add_marks()

        self.selection1 = pg.LinearRegionItem(movable=False)
        self.selection2 = pg.LinearRegionItem(movable=False)
        self.selection3 = pg.LinearRegionItem(movable=False)

        self.plot1.addItem(self.selection1)
        self.plot2.addItem(self.selection2)
        self.plot3.addItem(self.selection3)

        self.link_selections([self.selection1, self.selection2, self.selection3])

        # Select initial region
        self.update_selected_cycle(0)
        self.plot1.scene().sigMouseClicked.connect(self.on_click)

    def load_data(self, filename):
        time = []
        flow = []
        pressure = []
        volume = []
        pmus = []
        ref = []

        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                time.append(float(row['time']))
                flow.append(float(row['flow']))
                pressure.append(float(row['pressure']))
                volume.append(float(row['volume']))
                pmus.append(float(row['pmus']))
                ref.append(float(row['ref']))

        return np.array(time), np.array(flow), np.array(pressure), np.array(volume), np.array(pmus), np.array(ref)

    def plot_data(self):
        self.plot1.plot(self.time, self.pressure, pen=pg.mkPen([200, 200, 200], width=1))
        self.plot2.plot(self.time, self.flow, pen=pg.mkPen([200, 200, 200], width=1))
        self.plot3.plot(self.time, self.volume, pen=pg.mkPen([200, 200, 200], width=1))

    def add_marks(self):
        # add vertical lines for ins_marks and exp_marks on flow plot
        for mark in self.ins_marks:
            line = pg.InfiniteLine(
                pos=self.time[mark],
                angle=90,
                movable=False,
                pen=pg.mkPen('y', width=1, style=pg.QtCore.Qt.DotLine)
            )
            self.plot2.addItem(line)

    def update_selected_cycle(self, index):
        self.current_cycle_index = index
        if index < len(self.ins_marks) - 1:
            region = [self.time[self.ins_marks[index]], self.time[self.ins_marks[index + 1]]]
            self.selection1.setRegion(region)
            self.selection2.setRegion(region)
            self.selection3.setRegion(region)

        # update buttons to reflect stored asynchrony state
        self.double_trigger_button.setChecked(self.button_states[index].get('double_trigger', False))
        self.reverse_trigger_button.setChecked(self.button_states[index].get('reverse_trigger', False))
        self.early_cycling_button.setChecked(self.button_states[index].get('early_cycling', False))

    def on_click(self, event):
        mouse_point = self.plot1.vb.mapSceneToView(event.scenePos())
        x = mouse_point.x()
        for i in range(len(self.ins_marks) - 1):
            if self.time[self.ins_marks[i]] <= x <= self.time[self.ins_marks[i + 1]]:
                self.update_selected_cycle(i)
                break

    def link_selections(self, regions):
        def updateOtherRegions(region):
            edges = region.getRegion()
            for other in regions:
                if other != region:
                    other.setRegion(edges)

        for region in regions:
            region.sigRegionChanged.connect(updateOtherRegions)

    def update_button_state(self):
        self.button_states[self.current_cycle_index] = {
            'double_trigger': self.double_trigger_button.isChecked(),
            'reverse_trigger': self.reverse_trigger_button.isChecked(),
            'early_cycling': self.early_cycling_button.isChecked()
        }

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Waveform Viewer")
        self.setGeometry(100, 100, 1366, 768)

        self.plot_window = PlotWindow()
        self.setCentralWidget(self.plot_window)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setHighDpiScaleFactorRoundingPolicy(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
