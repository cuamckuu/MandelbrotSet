from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from numpy import *
import time

SIZE = 600

class View(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()
	
	def initUI(self):
		self.xmin = -2
		self.xmax = 0.5
		self.ymin = -1.25
		self.ymax = 1.25

		self.maxiter = 250

		self.last = None

		arr = self.mandel(SIZE, SIZE, self.maxiter, self.xmin, self.xmax, self.ymin, self.ymax)
		self.img = self.arrayToImage(arr)

		self.setMinimumSize(QSize(SIZE, SIZE))
		self.setMaximumSize(QSize(SIZE, SIZE))
		self.setWindowTitle("Mandelbrot")
		self.setMouseTracking(True)

		self.status = ("X", "Y")

		self.show()

	def mouseMoveEvent(self, e):
		self.setWindowTitle(str(self.coordToNum(e.x(), e.y())))
	
	def paintEvent(self, e):
		qp = QPainter()
		qp.begin(self)

		pix = QPixmap(self.img)
		qp.drawPixmap(QPoint(0,0), pix)
		
		qp.end()

	def mousePressEvent(self, e):
		self.last = self.coordToNum(e.x(), e.y())
	
	def mouseReleaseEvent(self, e):
		self.xmax, self.ymax = self.coordToNum(e.x(), e.y())
		self.xmin, self.ymin = self.last

		self.xmin, self.xmax = min(self.xmin, self.xmax), max(self.xmin, self.xmax) 
		self.ymin, self.ymax = min(self.ymin, self.ymax), max(self.ymin, self.ymax) 

		dist = sqrt((self.xmin-self.xmax)**2 + (self.ymin-self.ymax)**2)
		self.xmax = self.xmin + dist 
		self.ymax = self.ymin + dist

		self.maxiter += 15
		
		arr = self.mandel(SIZE, SIZE, self.maxiter, self.xmin, self.xmax, self.ymin, self.ymax)
		self.img = self.arrayToImage(arr)

		self.last = None

		self.update()

	def arrayToImage(self, arr):
		#rotate
		arr = arr.T 

		#add color
		arr = 255 - arr*7
		arr = require(arr, uint8, "C")
		img = dstack((arr % 255, arr * 2 % 255, arr*3 % 255))

		return QImage(img.data, SIZE, SIZE, QImage.Format_RGB888)

	def coordToNum(self, x, y):
		d_x = self.xmax - self.xmin
		d_y = self.ymax - self.ymin

		xNum = self.xmin + d_x * x/SIZE
		yNum = self.ymin + d_y * y/SIZE

		return (xNum, yNum)

	def mandel(self, n, m, itermax, xmin, xmax, ymin, ymax):
		start = time.time()

		ix, iy = mgrid[0:n, 0:m]
		x = linspace(xmin, xmax, n)[ix]
		y = linspace(ymin, ymax, m)[iy]
		c = x + complex(0, 1)*y
		del x, y 
		img = zeros(c.shape, dtype=int)
		ix.shape = n*m
		iy.shape = n*m
		c.shape = n*m
		z = copy(c)
		for i in range(itermax):
			if not len(z): break # all points have escaped
			
			z = z**2 + c
			#z = z**2 - 1
			#z = z**2 + complex(0.28, 0.0113)
			#z = z**2 + complex(0, 1)

			rem = abs(z) > 4.0
			img[ix[rem], iy[rem]] = i+1
			rem = ~rem
			z = z[rem]
			ix, iy = ix[rem], iy[rem]
			c = c[rem]
			img[img==0] = 101

		print("generate time: ", time.time()-start)
		return img

app = QApplication([])
view = View()
app.exec()