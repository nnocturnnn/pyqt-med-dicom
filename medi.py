from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtCore import Qt, QPoint, QLineF
from PyQt5 import QtWidgets,  QtCore, QtGui
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen, QColor
from PyQt5.QtWidgets import *
import pydicom
from pydicom.data import get_testdata_files
import matplotlib.pyplot as plt
import os
# import cv2
import numpy as np

lineage = True
resh = True
perek = True

class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)
    
    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0


    def setPhoto(self, pixmap=None):
        self._zoom = 0
        
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        print(self._zoom)
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)

    def lineage(self):
        global lineage
        self._zoom
        if lineage:
            lineage = False
            perc = 10
            zoomline = self._photo.pixmap().width()
            if zoomline > 256 and zoomline < 512:
                perc = 2
            elif zoomline > 512 and zoomline < 1024:
                perc = 3
            addedLine = QLineF(240/2,33/perc,240/2,223/perc)
            self._scene.addLine(addedLine, QColor(0, 0, 0)) 
            addedLine = QLineF(240/2,33/perc,230/2,33/perc)
            self._scene.addLine(addedLine, QColor(0, 0, 0)) 
            addedLine = QLineF(240/2,71/perc,230/2,71/perc)
            self._scene.addLine(addedLine, QColor(0, 0, 0)) 
            addedLine = QLineF(240/2,(71-19)/perc,235/2,(71-19)/perc)
            self._scene.addLine(addedLine, QColor(0, 0, 0)) 
            addedLine = QLineF(240/2,(71+19)/perc,235/2,(71+19)/perc)
            self._scene.addLine(addedLine, QColor(0, 0, 0)) 
            addedLine = QLineF(240/2,(71+38)/perc,230/2,(71+38)/perc)
            self._scene.addLine(addedLine, QColor(0, 0, 0)) 
            addedLine = QLineF(240/2,(71+38+38)/perc,230/2,(71+38+38)/perc)
            self._scene.addLine(addedLine, QColor(0, 0, 0)) 
            addedLine = QLineF(240/2,(71+38+19)/perc,235/2,(71+38+19)/perc)
            self._scene.addLine(addedLine, QColor(0, 0, 0)) 
            addedLine = QLineF(240/2,(71+38+38+38)/perc,230/2,(71+38+38+38)/perc)
            self._scene.addLine(addedLine, QColor(0, 0, 0)) 
            addedLine = QLineF(240/2,(71+38+38+19)/perc,235/2,(71+38+38+19)/perc)
            self._scene.addLine(addedLine, QColor(0, 0, 0)) 
            addedLine = QLineF(240/2,(71+38+38+38+19)/perc,230/2,(71+38+38+38+19)/perc)
            self._scene.addLine(addedLine, QColor(0, 0, 0)) 
            addedLine = QLineF(240/2,223/perc,230/2,223/perc)
            self._scene.addLine(addedLine, QColor(0, 0, 0))
           
            if perc == 2:
                needFont = self._scene.addText("5cm", QtGui.QFont("Times", 30)).setDefaultTextColor(QColor(255, 255, 255))
            elif perc == 1:
                needFont = self._scene.addText("10cm", QtGui.QFont("Times", 30)).setDefaultTextColor(QColor(0, 0, 0))
            else:
                needFont = self._scene.addText("20cm", QtGui.QFont("Times", 30)).setDefaultTextColor(QColor(0, 0, 0))
        else:
            self._scene.clear()
            self._scene = QtWidgets.QGraphicsScene(self)
            self._photo = QtWidgets.QGraphicsPixmapItem()
            self._scene.addItem(self._photo)
            self.setScene(self._scene)
            self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
            self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
            self.setFrameShape(QtWidgets.QFrame.NoFrame)
            lineage = True

    def pereh(self):
        perek = True
        if perek:
            perek = False
            addedLine = QLineF(self._photo.pixmap().width() / 2,0,self._photo.pixmap().width() / 2, self._photo.pixmap().width())
            self._scene.addLine(addedLine, QColor(0, 0, 0)) 
            addedLine = QLineF(0,self._photo.pixmap().width() / 2,self._photo.pixmap().width() , self._photo.pixmap().width() / 2)
            self._scene.addLine(addedLine, QColor(0, 0, 0))
            # rast = np.sqrt((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1))
            self._empty

    def resh(self, size):
        global resh
        if resh:
            resh = False
            q = size
            need = 38*q
            count_line = int(self._photo.pixmap().width() / need)
            count = 1
            start = (self._photo.pixmap().width() - (count_line * need)) / 2
            vLine = QLineF(start,0,start,256)
            self._scene.addLine(vLine,  QColor(0, 0, 0))
            vLine = QLineF(0,start,256,start)
            self._scene.addLine(vLine,  QColor(0, 0, 0))
            while count != count_line + 1:
                vLine = QLineF(start+need*count,0,start+need*count,256)
                self._scene.addLine(vLine,  QColor(0, 0, 0))
                vLine = QLineF(0,start+need*count,256,start+need*count)
                self._scene.addLine(vLine,  QColor(0, 0, 0))
                count += 1
        else:
            self._scene.clear()
            self._scene = QtWidgets.QGraphicsScene(self)
            self._photo = QtWidgets.QGraphicsPixmapItem()
            self._scene.addItem(self._photo)
            self.setScene(self._scene)
            self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
            self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
            self.setFrameShape(QtWidgets.QFrame.NoFrame)
            resh = True

    def zooms(self):
        self._zoom += 4


class Window(QtWidgets.QWidget):

    def __init__(self):
        super(Window, self).__init__()
        self.viewer = PhotoViewer(self)
        # 'Load image' button
        self.btnLoad = QtWidgets.QToolButton(self)
        self.btnLoad.setText('Load image')
        self.btnLoad.clicked.connect(self.loadImage)
        # Button to change from drag/pan to getting pixel info
        self.pere = QtWidgets.QToolButton(self)
        self.pere.setText('Перехрестя')
        self.pere.clicked.connect(self.viewer.pereh)
        self.line = QtWidgets.QToolButton(self)
        self.line.setText('Лiнiйка')
        self.line.clicked.connect(self.viewer.lineage)
        self.zoom = QtWidgets.QToolButton(self)
        self.zoom.setText('Збiльшення')
        self.zoom.clicked.connect(self.viewer.zooms)
        self.resh = QtWidgets.QToolButton(self)
        self.resh.setText('Решiтка')
        self.resh.clicked.connect(self.win_resh)
        self.editPixInfo = QtWidgets.QLineEdit(self)
        # self.editPixInfo.setReadOnly(True)
        self.viewer.photoClicked.connect(self.photoClicked)
        # Arrange layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.addWidget(self.viewer)
        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.setAlignment(QtCore.Qt.AlignLeft)
        HBlayout.addWidget(self.btnLoad)
        HBlayout.addWidget(self.pere)
        HBlayout.addWidget(self.line)
        HBlayout.addWidget(self.zoom)
        HBlayout.addWidget(self.resh)
        HBlayout.addWidget(self.editPixInfo)
        VBlayout.addLayout(HBlayout)

    def loadImage(self):
        self.editPixInfo.setText("112px")
#         fname = QFileDialog.getOpenFileName(self, 'Open file', 
#    'c:\\',"Image files (*.jpg *.gif *.dcm)")
#         dicomLoc = fname
#         ds = pydicom.read_file(dicomLoc)
#         dicomLoc = dicomLoc.replace('.dcm', '.jpg')
        # cv2.imwrite(dicomLoc, np.array(ds.pixel_array))
        self.viewer.setPhoto(QtGui.QPixmap("/Users/asydoruk/DICOM_set_16bits/brain_001.jpg"))

    def pixInfo(self):
        self.viewer.toggleDragMode()
    
    def win_resh(self):
        sizeresh = self.editPixInfo.text()
        if sizeresh:
            self.viewer.resh(int(sizeresh))
        else:
            self.viewer.resh(1)

    def photoClicked(self, pos):
        if self.viewer.dragMode()  == QtWidgets.QGraphicsView.NoDrag:
            self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))
    


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())