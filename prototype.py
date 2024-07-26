import os
import sys
import csv
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import numpy as np
import pandas as pd
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
        #self.time, self.flow, self.pressure, self.volume, self.pmus, self.ref = self.load_data('coletapcv_adequate.csv')
        #self.ins_marks, self.exp_marks = retrieve_parity_marks(self.volume * 10)

        full_df = pd.read_csv('c01r10c50.csv')
        df = full_df.iloc[:60000]

        self.time = df['time'].to_numpy()
        self.time = self.time - self.time[0]
        self.flow = df['flow'].to_numpy()
        self.pressure = df['pressure'].to_numpy()
        self.volume = df['volume'].to_numpy()
        self.pmus = df['pmus'].to_numpy()
        self.ref = df['ref'].to_numpy()
        self.inspiration = df['inspiration'].to_numpy()
        self.expiration = df['expiration'].to_numpy()

        self.ins_marks =  np.where(self.inspiration == 1)[0]
        self.exp_marks =  np.where(self.expiration == 1)[0]

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
        self.late_cycling_button = QtWidgets.QPushButton("Late Cycling")
        self.ineffective_effort_button = QtWidgets.QPushButton("Ineffective Effort")

        self.double_trigger_button.setCheckable(True)
        self.reverse_trigger_button.setCheckable(True)
        self.early_cycling_button.setCheckable(True)
        self.late_cycling_button.setCheckable(True)
        self.ineffective_effort_button.setCheckable(True)

        button_layout.addWidget(self.double_trigger_button)
        button_layout.addWidget(self.reverse_trigger_button)
        button_layout.addWidget(self.early_cycling_button)
        button_layout.addWidget(self.late_cycling_button)
        button_layout.addWidget(self.ineffective_effort_button)
        button_layout.addStretch()  # push buttons to the top

        self.double_trigger_button.clicked.connect(self.update_button_state)
        self.reverse_trigger_button.clicked.connect(self.update_button_state)
        self.early_cycling_button.clicked.connect(self.update_button_state)
        self.late_cycling_button.clicked.connect(self.update_button_state)
        self.ineffective_effort_button.clicked.connect(self.update_button_state)

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
        """
        # add vertical lines for ins_marks and exp_marks on flow plot
        for mark in self.ins_marks:
            line = pg.InfiniteLine(
                pos=self.time[mark],
                angle=90,
                movable=False,
                pen=pg.mkPen('y', width=1, style=pg.QtCore.Qt.DotLine)
            )
            self.plot2.addItem(line)
        """

        ins_markers_p2 = pg.ScatterPlotItem(
            x=self.time[self.ins_marks],
            y=self.flow[self.ins_marks],
            symbol='t1',
            pen='y',
            brush='y',
            size=8
        )
        exp_markers_p2 = pg.ScatterPlotItem(
            x=self.time[self.exp_marks],
            y=self.flow[self.exp_marks],
            symbol='t',
            pen='y',
            brush='y',
            size=8
        )
        self.plot2.addItem(ins_markers_p2)
        self.plot2.addItem(exp_markers_p2)


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
        self.late_cycling_button.setChecked(self.button_states[index].get('late_cycling', False))
        self.ineffective_effort_button.setChecked(self.button_states[index].get('ineffective_effort', False))

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
            'early_cycling': self.early_cycling_button.isChecked(),
            'late_cycling': self.late_cycling_button.isChecked(),
            'ineffective_effort': self.ineffective_effort_button.isChecked()
        }

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        with open('style.qss', 'r') as file:
            style_sheet = file.read()
            self.setStyleSheet(style_sheet)

        self.setWindowTitle("Waveform Viewer")
        self.setGeometry(100, 100, 1600, 900)

        self.plot_window = PlotWindow()
        self.setCentralWidget(self.plot_window)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setHighDpiScaleFactorRoundingPolicy(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
