from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint, QLineF
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import (
    QToolButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
)


BLACK_COLOR = QColor(0, 0, 0)
WHITE_COLOR = QColor(255, 255, 255)
BACKGROUND_COLOR = QColor(30, 30, 30)
NO_DRAG = QtWidgets.QGraphicsView.NoDrag
SCROLL_HAND_DRAG = QtWidgets.QGraphicsView.ScrollHandDrag
FRAME_NO_SHAPE = QtWidgets.QFrame.NoFrame
DEFAULT_ZOOM_FACTOR_IN = 1.25
DEFAULT_ZOOM_FACTOR_OUT = 0.8
LINEAGE_WIDTH_THRESHOLD_1 = 256
LINEAGE_WIDTH_THRESHOLD_2 = 512
LINEAGE_WIDTH_THRESHOLD_3 = 1024
DEFAULT_LINEAGE_PERC = 10
LINEAGE_PERC_1 = 2
LINEAGE_PERC_2 = 3
GRID_LINE_OFFSET = 38
FONT_SIZE = 30
TEXT_5CM = "5cm"
TEXT_10CM = "10cm"
TEXT_20CM = "20cm"
PIXEL_INFO_DEFAULT_TEXT = "112px"


class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QPoint)

    def __init__(self, parent=None):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(BACKGROUND_COLOR))
        self.setFrameShape(FRAME_NO_SHAPE)
        self._lineage_state = False
        self._resh_state = False
        self._perek_state = False

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
                factor = min(
                    viewrect.width() / scenerect.width(),
                    viewrect.height() / scenerect.height(),
                )
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(SCROLL_HAND_DRAG)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(NO_DRAG)
            self._photo.setPixmap(QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            factor = (
                DEFAULT_ZOOM_FACTOR_IN
                if event.angleDelta().y() > 0
                else DEFAULT_ZOOM_FACTOR_OUT
            )
            self._zoom += 1 if factor > 1 else -1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == SCROLL_HAND_DRAG:
            self.setDragMode(NO_DRAG)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(SCROLL_HAND_DRAG)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)

    def toggleLineage(self):
        self._lineage_state = not self._lineage_state
        if self._lineage_state:
            self.drawLineage()
        else:
            self.clearScene()

    def drawLineage(self):
        zoomline = self._photo.pixmap().width()
        perc = DEFAULT_LINEAGE_PERC
        if zoomline > LINEAGE_WIDTH_THRESHOLD_1:
            perc = (
                LINEAGE_PERC_1
                if zoomline < LINEAGE_WIDTH_THRESHOLD_2
                else LINEAGE_PERC_2 if zoomline < LINEAGE_WIDTH_THRESHOLD_3 else perc
            )
        for i in range(11):
            offset = GRID_LINE_OFFSET * (i // 2) if i else 0
            self._scene.addLine(
                QLineF(120, 33 / perc + offset, 115, 33 / perc + offset),
                BLACK_COLOR,
            )
            if i % 2 == 0:
                self._scene.addLine(
                    QLineF(
                        120, 33 / perc + offset, 120, 33 / perc + offset + 190 / perc
                    ),
                    BLACK_COLOR,
                )
        text = {LINEAGE_PERC_1: TEXT_5CM, LINEAGE_PERC_2: TEXT_10CM}.get(
            perc, TEXT_20CM
        )
        self._scene.addText(text, QtGui.QFont("Times", FONT_SIZE)).setDefaultTextColor(
            WHITE_COLOR if perc == LINEAGE_PERC_1 else BLACK_COLOR
        )

    def togglePereh(self):
        self._perek_state = not self._perek_state
        if self._perek_state:
            self.drawPereh()

    def drawPereh(self):
        self._scene.addLine(
            QLineF(
                self._photo.pixmap().width() / 2,
                0,
                self._photo.pixmap().width() / 2,
                self._photo.pixmap().height(),
            ),
            BLACK_COLOR,
        )
        self._scene.addLine(
            QLineF(
                0,
                self._photo.pixmap().height() / 2,
                self._photo.pixmap().width(),
                self._photo.pixmap().height() / 2,
            ),
            BLACK_COLOR,
        )

    def toggleResh(self, size):
        self._resh_state = not self._resh_state
        if self._resh_state:
            self.drawResh(size)
        else:
            self.clearScene()

    def drawResh(self, size):
        need = GRID_LINE_OFFSET * size
        count_line = int(self._photo.pixmap().width() / need)
        start = (self._photo.pixmap().width() - (count_line * need)) / 2
        for i in range(count_line + 1):
            offset = start + need * i
            self._scene.addLine(
                QLineF(offset, 0, offset, self._photo.pixmap().height()),
                BLACK_COLOR,
            )
            self._scene.addLine(
                QLineF(0, offset, self._photo.pixmap().width(), offset), BLACK_COLOR
            )

    def clearScene(self):
        self._scene.clear()
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)

    def zoomIn(self):
        self._zoom += 4


class Window(QtWidgets.QWidget):

    def __init__(self):
        super(Window, self).__init__()
        self.viewer = PhotoViewer(self)
        self.setupUI()

    def setupUI(self):
        self.btnLoad = self.createButton("Load image", self.loadImage)
        self.pere = self.createButton("Перехрестя", self.viewer.togglePereh)
        self.line = self.createButton("Лiнiйка", self.viewer.toggleLineage)
        self.zoom = self.createButton("Збiльшення", self.viewer.zoomIn)
        self.resh = self.createButton("Решiтка", self.applyResh)
        self.editPixInfo = QLineEdit(self)
        self.viewer.photoClicked.connect(self.updatePixelInfo)

        VBlayout = QVBoxLayout(self)
        VBlayout.addWidget(self.viewer)
        HBlayout = QHBoxLayout()
        HBlayout.setAlignment(Qt.AlignLeft)
        HBlayout.addWidget(self.btnLoad)
        HBlayout.addWidget(self.pere)
        HBlayout.addWidget(self.line)
        HBlayout.addWidget(self.zoom)
        HBlayout.addWidget(self.resh)
        HBlayout.addWidget(self.editPixInfo)
        VBlayout.addLayout(HBlayout)

    def createButton(self, text, callback):
        button = QToolButton(self)
        button.setText(text)
        button.clicked.connect(callback)
        return button

    def loadImage(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Open file", "", "Image files (*.dcm)"
        )
        if fname:
            self.viewer.setPhoto(QPixmap(fname))
            self.edit
