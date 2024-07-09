import sys
import csv
from PyQt5 import QtWidgets
import pyqtgraph as pg
import numpy as np
from utils import retrieve_parity_marks

# Set background to white
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
#pg.setConfigOptions(antialias=True)

class PlotWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Load data
        self.time, self.flow, self.pressure, self.volume, self.pmus, self.ref = self.load_data('coletapcv_adequate.csv')

        # Create a layout
        layout = QtWidgets.QVBoxLayout()

        # Create plots
        self.plot1 = pg.PlotWidget(title="Flow")
        self.plot2 = pg.PlotWidget(title="Pressure")
        self.plot3 = pg.PlotWidget(title="Volume")

        # Show grids
        self.plot1.showGrid(x=True, y=True)
        self.plot2.showGrid(x=True, y=True)
        self.plot3.showGrid(x=True, y=True)

         # Link the views
        self.plot2.setXLink(self.plot1)
        self.plot3.setXLink(self.plot1)

        # Add plots to layout
        layout.addWidget(self.plot1)
        layout.addWidget(self.plot2)
        layout.addWidget(self.plot3)

        # Set layout
        self.setLayout(layout)

        # Plot data
        self.plot_data()

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
        self.plot1.plot(self.time, self.flow, pen=pg.mkPen('k', width=2))
        self.plot2.plot(self.time, self.pressure, pen=pg.mkPen('k', width=2))
        self.plot3.plot(self.time, self.volume, pen=pg.mkPen('k', width=2))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = PlotWindow()
    main.show()
    sys.exit(app.exec_())
