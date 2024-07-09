import os
import sys
import csv
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import numpy as np
from utils import retrieve_parity_marks

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

# Set background to white
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
#pg.setConfigOptions(antialias=True)

class PlotWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Load data
        self.time, self.flow, self.pressure, self.volume, self.pmus, self.ref = self.load_data('coletapcv_adequate.csv')
        self.ins_marks, self.exp_marks = retrieve_parity_marks(self.volume * 10)

        plot_layout = QtWidgets.QVBoxLayout()

        self.plot1 = pg.PlotWidget(title="Pressure")
        self.plot2 = pg.PlotWidget(title="Flow")
        self.plot3 = pg.PlotWidget(title="Volume")

        self.plot1.showGrid(x=True, y=True)
        self.plot2.showGrid(x=True, y=True)
        self.plot3.showGrid(x=True, y=True)

        self.plot2.setXLink(self.plot1)
        self.plot3.setXLink(self.plot1)

        plot_layout.addWidget(self.plot1)
        plot_layout.addWidget(self.plot2)
        plot_layout.addWidget(self.plot3)

        button_layout = QtWidgets.QVBoxLayout()
        self.zoom_in_button = QtWidgets.QPushButton("Zoom In")
        self.zoom_out_button = QtWidgets.QPushButton("Zoom Out")
        self.smooth_button = QtWidgets.QPushButton("Smooth")

        button_layout.addWidget(self.zoom_in_button)
        button_layout.addWidget(self.zoom_out_button)
        button_layout.addWidget(self.smooth_button)
        button_layout.addStretch()  # Add stretch to push buttons to the top

        # horizontal layout to contain both plot layout and button layout
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(plot_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.plot_data()
        self.add_marks()

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
        self.plot1.plot(self.time, self.pressure, pen=pg.mkPen('b', width=2))
        self.plot2.plot(self.time, self.flow, pen=pg.mkPen('b', width=2))
        self.plot3.plot(self.time, self.volume, pen=pg.mkPen('b', width=2))

    def add_marks(self):
        # Add vertical lines for ins_marks and exp_marks on Volume plot
        for mark in self.ins_marks:
            line = pg.InfiniteLine(pos=self.time[mark], angle=90, movable=False, pen=pg.mkPen('r', width=2, style=pg.QtCore.Qt.DotLine))
            self.plot2.addItem(line)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
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
