#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  9 17:55:28 2019

@author: ulises
"""


from tkinter import Canvas, Tk, Checkbutton, Button, IntVar, StringVar, Menu,\
			Message, messagebox, filedialog, Entry, Text, Frame, LEFT, RIGHT, X
#from sys import platform
from cv2 import pointPolygonTest, VideoCapture, CAP_PROP_FRAME_COUNT,\
			CAP_PROP_POS_FRAMES, drawContours

from os import curdir
from os.path import abspath

#import numpy as np
from numpy import zeros, uint8
from numpy import copy as npcopy
from numpy import load as npload
from numpy import save as npsave
from PIL import Image, ImageTk
from time import localtime

#%% Programa

#TODO list
"""
\begin{itemize}

\item selección multiple \check
\item Trabajar en pantalla completa \not se puede hacer zoom y arrastrar la imagen con algunos bugs
\item Poder Cargar Nuevos Videos \check
\item Modificar Grosor de contornos \check
\item agregar saltos \pm 1,10,100 \check
\item hacer zoom y arrastrar imagen \check

"""



listaMalezas = ['STEME',
				'LAMAM',
				'COPDI',
				'CULAU',
				'AVEFA',
				'LOLMU',
				'POAAN',
				'ZEAMX',
				'TRIAX',
				'GLYMX']


nombresAMostrar = ['Caapiquí - Stellaria media',
					'Ortiga mansa - Lamium amplexicaule',
					'Mastuerzo - Coronopus didymus',
					'Botón de oro - Cotula australis',
					'Avena guacha - Avena fatua',
					'Raigrás anual - Lolium multiflorum',
					'Pastito de invierno - Poa annua',
					'Maíz - Zea mays',
					'Trigo - Triticum aestivum',
					'Soja - Glycine max']




class MyMenu(Menu):
	def __init__(self,m,Gui):
		self.Gui=Gui
		super(MyMenu,self).__init__(master=m)
		self.filemenu = Menu(self, tearoff=0)
		self.filemenu.add_command(label="CambiarVideo", command=self.CambiarVideo)
		self.filemenu.add_command(label="Save", command=self.Gui.saveDateTime)
		self.filemenu.add_command(label="Save as...", command=self.Gui.saveDataAs)
		self.filemenu.add_command(label="Close", command=self.Gui._exit)
		self.add_cascade(label="File", menu=self.filemenu)

		self.helpmenu = Menu(self, tearoff=0)
		self.helpmenu.add_command(label="Help Index", command=self.p)
		self.helpmenu.add_command(label="About...", command=self.p)
		self.add_cascade(label="Help", menu=self.p)
	def CambiarVideo(self):
		self.Gui.__reinit__()
	def p(self):
		print('cambiarDeVideo')
		pass

class MyCanvas():
	def __init__(self,master,gui):
		self.Gui = gui
		self._setCanvas(master)

	def _setCanvas(self,master):
		""" Inicializo el Canvas"""
		self.canvas = Canvas(master,width=1000,height=1000)
		self.canvas.pack(padx=2, pady=2,expand=True)
		self.canvas.update()
		self.width = 1000
		self.height= 1000
		self.imscale = 1.0  # scale for the canvaas image
		self.delta = 1.3  # zoom magnitude
		self._CanvasBinds()
		self.container = self.canvas.create_rectangle(0, 0, self.width,
											self.height, width=0)

	def _CanvasBinds(self):
		self.canvas.bind("<Button-1>", 		self.onClick)
		self.canvas.bind("<Shift-Button-1>", 	self.onClickM)#multiple
		self.canvas.bind('<Configure>', 		self.show_image)  # canvas is resized
		self.canvas.bind('<ButtonPress-3>', 	self.move_from)
		self.canvas.bind('<B3-Motion>',		self.move_to)
		self.canvas.bind('<MouseWheel>', 	self.wheel)  # with Windows and MacOS, but not Linux
		self.canvas.bind('<Button-5>', 		self.wheel)  # only with Linux, wheel scroll down
		self.canvas.bind('<Button-4>', 		self.wheel)

	def onClick(self,eventorigin):
		if len(self.Gui.selectedContNumber)>0:
			self.Gui.checkChecks()
		""" Leo Click del mouse y selecciono recuadro"""
		self.xEv = eventorigin.x
		self.yEv = eventorigin.y
		thisConts =self.Gui.thisConts
		dists = zeros(len(thisConts))
		self.Gui._drawContCon_y_sinDatos()
		realX = (self.xEv-self.ImageX +\
					self.canvas.canvasx(0))/self.imscale
		realY = (self.yEv-self.ImageY +\
					self.canvas.canvasy(0))/self.imscale
		#print(self.myCanvas.xEv,realX);
		#print(self.myCanvas.yEv,realY)
		for i in range(len(thisConts)):
			cont = thisConts[i]
			dists[i] = pointPolygonTest(cont,
										(realX, realY),True)
		if any(dists>0):
			dists[dists<=0] = 1e10
			selectedContNumber = dists.argmin()
			self.Gui.selectedContNumber = [selectedContNumber]
			self.Gui.clearChecks()
			if selectedContNumber in self.Gui.contsConDatos.keys():
				self.Gui.restoreChecks(selectedContNumber)
				self.Gui.restoreOtherWeed(selectedContNumber)
			self.Gui._drawContCon_y_sinDatos()
		else:
			self.Gui.clearChecks()
			self.Gui.selectedContNumber = []
		self.Gui.clearOtherWeed()
		self.Gui._updateLabel()
		self._refreshCanvas()

	def onClickM(self,eventorigin): #"""multiple selections"""
		self.xEv = eventorigin.x
		self.yEv = eventorigin.y
		#""" Leo Click del mouse y selecciono recuadro"""
		thisConts =self.Gui.thisConts
		dists = zeros(len(thisConts))
		self.Gui._drawContCon_y_sinDatos()
		realX = (self.xEv-self.ImageX +\
					self.canvas.canvasx(0))/self.imscale
		realY = (self.yEv-self.ImageY +\
					self.canvas.canvasy(0))/self.imscale
		for i in range(len(thisConts)):
			cont = thisConts[i]
			dists[i] = pointPolygonTest(cont,
										(realX, realY),True)
		if any(dists>0):
			dists[dists<=0] = 1e10
			ThisSelectedContNumber = dists.argmin()
			self.Gui.selectedContNumber .append(ThisSelectedContNumber)
			self.Gui.clearChecks()

			self.Gui._drawContCon_y_sinDatos()
		else:
			self.Gui.clearChecks()
			self.Gui.selectedContNumber = []
		self.Gui.clearOtherWeed()
		self.Gui._updateLabel()
		self._refreshCanvas()



	def move_from(self, event):
		''' Remember previous coordinates for scrolling with the mouse '''
		self.canvas.scan_mark(event.x, event.y)

	def move_to(self, event):
		''' Drag (move) canvas to the new position '''
		self.canvas.scan_dragto(event.x, event.y, gain=1)
		self.show_image()  # redraw the image

	def wheel(self, event):
		''' Zoom with mouse wheel '''
		canvas = self.canvas
		x = canvas.canvasx(event.x)
		y = canvas.canvasy(event.y)
		bbox = canvas.bbox(self.container)  # get image area
		if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
		else: return  # zoom only inside image area
		scale = 1.0
		# Respond to Linux (event.num) or Windows (event.delta) wheel event
		if event.num == 5 or event.delta == -120:  # scroll down
			i = min(self.width, self.height)
			if int(i * self.imscale) < 30: return  # image is less than 30 pixels
			self.imscale /= self.delta
			scale		/= self.delta
		if event.num == 4 or event.delta == 120:  # scroll up
			i = min(canvas.winfo_width(), canvas.winfo_height())
			if i < self.imscale: return  # 1 pixel is bigger than the visible area
			self.imscale *= self.delta
			scale		*= self.delta
		canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
		self.canvas = canvas
		self.show_image()


	def show_image(self, event=None):
		''' Show image on the Canvas '''
		canvas=self.canvas
		bbox1 = canvas.bbox(self.container)  # get image area
		# Remove 1 pixel shift at the sides of the bbox1
		bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
		bbox2 = (canvas.canvasx(0),  # get visible area of the canvas
				 canvas.canvasy(0),
				 canvas.canvasx(canvas.winfo_width()),
				 canvas.canvasy(canvas.winfo_height()))
		bbox = [int(min(bbox1[0], bbox2[0])), int(min(bbox1[1], bbox2[1])),  # get scroll region box
				int(max(bbox1[2], bbox2[2])), int(max(bbox1[3], bbox2[3]))]
		if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
			bbox[0] = bbox1[0]
			bbox[2] = bbox1[2]
		if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
			bbox[1] = bbox1[1]
			bbox[3] = bbox1[3]
		canvas.configure(scrollregion=bbox)  # set scroll region
		x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
		y1 = max(bbox2[1] - bbox1[1], 0)
		x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
		y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
		if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
			x = min(int(x2 / self.imscale), self.width)   # sometimes it is larger on 1 pixel...
			y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not
			image = Image.fromarray(self.Gui.im).crop((int(x1 / self.imscale),
											 int(y1 / self.imscale), x, y))
			imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
			self.ImageX =max(bbox2[0], bbox1[0])
			self.ImageY =max(bbox2[1], bbox1[1])
			imageid = canvas.create_image(self.ImageX, self.ImageY,
											   anchor='nw', image=imagetk)
			canvas.lower(imageid)  # set image into background
			canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection
			self.canvas =canvas
	def _refreshCanvas(self):
		""" Dibujo en el canvas la nueva imagen """

		self.canvas.image = Image.fromarray(self.Gui.im)
		self.canvas.update()
		self.show_image()


class MyVideo():
	def __init__(self,Gui):
		self.Gui=Gui

	def setContourWidth(self,frame,redFunc,augFunc):
		self.btnZoomIn = Button(frame, text='+', command=augFunc)
		self.btnZoomOut= Button(frame, text='-', command=redFunc)
		self.btnZoomIn.pack()
		self.btnZoomOut.pack(side='bottom')

	def  setBotonesenFrame(self,frame):
		self.btn_bcien = Button(frame,text='<<<(x100)'	,command=self.mr_b100 )
		self.btn_bdiez = Button(frame,text='<<(x10)' 	,command=self.mr_b10  )
		self.btn_buno  = Button(frame,text='<(x1)'		,command=self.mr_b1   )
		self.btn_funo  = Button(frame,text='>(x1)'		,command=self.mr_f1   )
		self.btn_fdiez = Button(frame,text='>>(x10)' 	,command=self.mr_f10  )
		self.btn_fcien = Button(frame,text='>>>(x100)'	,command=self.mr_f100 )

		self.btn_bcien.place({'in':frame,'x':500,'y':5,'width':90 ,'height':20})
		self.btn_bdiez.place({'in':frame,'x':595,'y':5,'width':65 ,'height':20})
		self.btn_buno .place({'in':frame,'x':665,'y':5,'width':45 ,'height':20})
		self.btn_funo .place({'in':frame,'x':715,'y':5,'width':45 ,'height':20})
		self.btn_fdiez.place({'in':frame,'x':770,'y':5,'width':70 ,'height':20})
		self.btn_fcien.place({'in':frame,'x':845,'y':5,'width':90 ,'height':20})


	def mr_b100(self):
		self.moveRel(-100)
	def mr_b10(self):
		self.moveRel(-10)
	def mr_b1(self):
		self.moveRel(-1)
	def mr_f100(self):
		self.moveRel(100)
	def mr_f10(self):
		self.moveRel(10)
	def mr_f1(self):
		self.moveRel(1)

	def moveRel(self,desp):
		self.Gui.checkChecks()
		self.Gui.saveData()
		actualPos = self.actualPos()
		newPos = actualPos+desp
		newPos = newPos if newPos>0 else 0
		newPos = newPos if newPos<self.nFrames else self.nFrames
		self.goto(newPos)



	def openVid(self,direc):
		returns = dict()
		MsgBox = messagebox.showinfo('Abrir Video','Seleccione el video a trabajar',
										icon = 'warning')
		dat = filedialog.askopenfilename(initialdir= direc,
										 title = "Seleccionar video")
		direc = '/'.join(dat.split('/')[:-1]) +'/'
		returns['newDirec'] =direc
		self.capture = VideoCapture(dat)
		self.name = dat
		if not self.capture.isOpened():
			MsgBox = messagebox.askretrycancel('Error','No se pudo cargar el video'+\
										'volver a intentar o cerrar?',
										icon = 'warning')
			if MsgBox == 'retry':
				self.openVid()
			else:
				returns['destroy']=True
		self.nFrames=self.capture.get(CAP_PROP_FRAME_COUNT)
		return returns

	def actualPos(self):
		return int(self.capture.get(CAP_PROP_POS_FRAMES))-1


	def goto(self,desiredFrame):
		try:
			if desiredFrame!=int(self.actualPos()) and (desiredFrame<self.nFrames):
				self.capture.set(CAP_PROP_POS_FRAMES, desiredFrame)

				self.Gui.NextImage()
		except:
			print('Fallo')
			pass



class GUI(Tk):
	def __init__(self,listaDePlantas,nombres):
		super(GUI,self).__init__()
		self.listaPlantas 	= listaDePlantas
		self.nombres 		= nombres
		#self 			= Tk()
		self.setTitle('GUI de Clasificación')
		self.minsize(width=1200,height=600)
		#self.maxsize(width=1500,height=900)
		self.ActualPos 	= None
		self.video 		= MyVideo(self)
		self.strVar 		= StringVar(None)
		self.otherWeedVar 	= StringVar(None)
		self.contWidth=3
		self.dir = abspath(curdir)
		#frames
		self.LEFTFrame  = Frame(self)
		self.RIGHTFrame = Frame(self)
		self.DRFrame = Frame(self.RIGHTFrame)
		self.CFrame = Frame(self.LEFTFrame)
		self.LEFTFrame.pack(side='left',expand=True); self.RIGHTFrame.pack(side='right')
		self.DRFrame.pack(side='bottom'); self.CFrame.pack(side='right')
		#Inicializo Sub-Objetos, abro videos etc
		self.myCanvas = MyCanvas(self.LEFTFrame,self)
		self.myMenu   = MyMenu(self,self)
		self.config(menu=self.myMenu)

		self._setChecks()
		self._setOtherWeed()
		self._setButtons()
		self._setContours()


		self.__reinit__()

	def __reinit__(self):
		self.im = zeros((100,100,3),dtype=uint8)
		self.contsConDatos = {}
		self.selectedContNumber =[]
		self._openVidAndConts()
		#[chck1,chck2....chck#n] donde #n es el largo de malezas
		#[btnPass,btnConfirm,btnExit,btnGuardar]
		self.Label()
		self.NextImage()
		self.dataClasif = [['nFrame','ListaBlob_Maleza',listaMalezas]]


	def tk(self):
		return self
	def setTitle(self,title):
		self.title(title)
	
	#--------------------------------------------------------------------------
	""" Inicializaciones"""
	#--------------------------------------------------------------------------
	
	def Label(self):
		self.entry = Entry(self.LEFTFrame,textvariable=self.strVar)
		self.entry.place({'in':self.LEFTFrame,'x':5,'y':5,'width':40,'height':20})
		self.entry.bind("<Return>",self.onEnter)
		self.text = Text(self.LEFTFrame, state='normal')
		self.text.insert('end', int(self.video.nFrames))
		self.text.place({'x':40,'y':5,'width':50,'height':20})
		self.text.configure(state='disabled')
		self.video.setBotonesenFrame(self.LEFTFrame)

	def _openVidAndConts(self):
		self._openVid()
		self._openConts()
		if not (self.video.name.split('/')[-1].split('.')[0] ==self.contname.split('/')[-1].split('.')[0]):
			MsgBox = messagebox.askquestion ('Ojo','El archivo de video que'+\
									' elegiste no tiene el mismo nombre que '+\
									'el de contours.\n Queres seguir igual?'+\
									'sino volvé a elegir',
										icon = 'warning')
			if MsgBox== 'yes':
				pass
			else:
				self._openVidAndConts()


	def _openVid(self):
		rets = self.video.openVid(self.dir)
		if 'newDirec' in rets.keys():
			self.dir=rets['newDirec']
		if 'destroy' in rets.keys():
			if rets['destroy']==True:
				self.destroy()


	def _openConts(self):
		MsgBox = messagebox.showinfo('Abrir Archivo de Contours','Seleccione el archivo a trabajar',
										icon = 'warning')
		dat = filedialog.askopenfilename(initialdir= self.dir,
										 title = "Seleccionar archivo")
		self.dir = '/'.join(dat.split('/')[:-1]) +'/'
		self.contname = dat
		try:
			self.contours=npload(dat,allow_pickle=True)
		except:
			MsgBox = messagebox.askretrycancel('Error','No se pudo cargar el archivo'+\
										' volver a intentar o cerrar?',
										icon = 'warning')
			if MsgBox == 'retry':
				self._openConts()
			else:
				self.destroy()


	def _setChecks(self):
		self.checkList =[]
		for i in range(len(self.listaPlantas)):
			exec("self.chVar"+ str(i) +" = IntVar()")
			exec("self.chck" + str(i) +"=Checkbutton("+'self.RIGHTFrame'+\
								",text='"+self.nombres[i]+\
								"',var=self.chVar"+str(i)+",anchor='w')")
			exec("self.chck"+str(i)+".pack(fill='x',padx=10,expand=False)")

			self.checkList.append( exec("self.chck"+str(i)))
	
	def _setOtherWeed(self):
		self.otherWeedEntry = Entry(self.RIGHTFrame,textvariable=self.otherWeedVar)
		self.otherWeedEntry.pack(expand=False)
		
		
	def _setButtons(self):
		self.DRF1=Frame(self.DRFrame); self.DRF1.pack()
		self.DRF2=Frame(self.DRFrame); self.DRF2.pack(side='bottom')
		self.DRF3=Frame(self.DRFrame); self.DRF3.pack(side='bottom')

		self.btnConfirm = Button(self.DRF1, text= 'Confirmar Selecciones',
								  command=self._confirm)
		self.btnConfirm.pack(fill='x',pady=10)

		self.btnGuardar = Button(self.DRF3, text= 'Guardar Datos',
								  command=self.saveDateTime)
		self.btnGuardar.pack(side='left')
		self.btnCargar  = Button(self.DRF3, text='Cargar Datos',
								  command=self.CargarDatos)
		self.btnCargar.pack(side='left')

# 		self.btnPass    = Button(self.DRF1, text= 'Saltar Imagen',
# 								  command=self._pass)
# 		self.btnPass.pack()

		self.btnExit    = Button(self.DRF2, text= 'Salir del programa',
								  command=self._exit)
		self.btnExit.pack(fill='x')


		self.btnList= [self.btnCargar,self.btnConfirm,
					   self.btnGuardar,self.btnExit]

	def _setContours(self):
		self.video.setContourWidth(self.CFrame, self.contReduce,
									   self.contAugment)


	#--------------------------------------------------------------------------
	"""Fin inicializaciones"""
	#--------------------------------------------------------------------------
	#--------------------------------------------------------------------------
	"""Label Functions"""
	#--------------------------------------------------------------------------

	def contReduce(self):
		if self.contWidth > 0:
			self.contWidth -=1
		else:
			pass
		self._drawContCon_y_sinDatos()
		self.myCanvas._refreshCanvas()

	def contAugment(self):
		if self.contWidth<10:
			self.contWidth +=1
			self._drawContCon_y_sinDatos()
			self.myCanvas._refreshCanvas()
		else:
			pass

	def onEnter(self,eventorigin):
		desiredFrame = int(self.strVar.get())
		self.video.goto(desiredFrame)

	#--------------------------------------------------------------------------
	"""Canvas Functions"""
	#--------------------------------------------------------------------------


	def _drawContCon_y_sinDatos(self):
		""" Dibujo los contornos"""
		if self.contWidth > 0 :
			self.im = drawContours(npcopy(self.thisFrame),self.thisConts,
											 -1,(255,0,0),thickness=self.contWidth)
			contsConDatos = self.contsConDatos
			selContN=self.selectedContNumber
			if len(contsConDatos)>0:
				for i in contsConDatos.keys():
					if (len(contsConDatos[i][0])>0 or contsConDatos[i][1]!=''):
						self.im =  drawContours(self.im,self.thisConts, i
										 ,(0,0,255),thickness=self.contWidth)
			if len(selContN) >0 :
				for c in selContN:
					self.im =  drawContours(self.im,self.thisConts,c,
										   (0,255,0),thickness=self.contWidth)
		else:
			self.im = npcopy(self.thisFrame)



	def NextImage(self): #Busco La Siguiente Imagen del video
		self.contsConDatos={} #Si abro el siguiente frame, no tengo datos
		self.selectedContNumber=[]
		ret, self.im = self.video.capture.read()
		if not ret:
			msg = Message(self,text="no hay más imagenes. Saliendo")
			msg.pack()
			self._exit()
		self.thisFrame = npcopy(self.im)
		self.ActualPos = self.video.actualPos()
		self.thisConts = self.contours[self.ActualPos]
		self._drawContCon_y_sinDatos()

		self.myCanvas._refreshCanvas()
		self._updateLabel()


	

	#--------------------------------------------------------------------------
	""" Fin Funciones Canvas"""
	#--------------------------------------------------------------------------
	
	#--------------------------------------------------------------------------
	""" Acciones de Checks"""
	#--------------------------------------------------------------------------
	def checkChecks(self):
		self.plantasInThisCont = zeros(len(self.listaPlantas))
		for i in range(len(self.listaPlantas)):
			exec("self.plantasInThisCont[i] = self.chVar"+str(i) +".get()")
		weed = self.otherWeedVar.get()
		selConList =self.selectedContNumber
		if len(selConList)>0:
			for con in selConList:
				if self.plantasInThisCont.any():
					self.contsConDatos[con] = [self.plantasInThisCont,weed]
				else:
					self.contsConDatos[con] = [[],weed]


	def clearChecks(self):
		for i in range(len(self.listaPlantas)):
			exec("self.chVar"+str(int(i))+".set(0) ")
	
	def clearOtherWeed(self):
		self.otherWeedEntry.delete(0,30)
		
		
	def restoreChecks(self,number):
		checked = self.contsConDatos[number][0]
		for i in range(len(checked)):
			if checked[i]==1:
				exec("self.chVar"+str(int(i))+".set(1) ")

	def restoreOtherWeed(self,number):
		self.contsConDatos[number][1]
		self.entry.insert('insert',self.contsConDatos[number][1])

	
	#--------------------------------------------------------------------------
	""" Fin Acciones de Checks"""
	#--------------------------------------------------------------------------

	
	#--------------------------------------------------------------------------
	""" Acciones de los botones"""
	#--------------------------------------------------------------------------
	def _updateLabel(self):
		self.entry.delete(0,10)
		self.entry.insert('insert',int(self.ActualPos))

	def _pass(self):
		self.NextImage()
	
	def _confirm(self):
		self.checkChecks()
		self.saveData()
		self.NextImage()
	


	#--------------------------------------------------------------------------
	""" Saves y Loads"""
	#--------------------------------------------------------------------------

	def saveData(self):
		self.dataClasif.append([self.ActualPos, self.contsConDatos])
		npsave('tmp',self.dataClasif, allow_pickle=True)
	
	def saveDateTime(self):
		q= localtime()
		nombre = str(q[2])+'_'+str(q[1])+'_'+str(q[0])+'_'+\
					str(q[3])+'_'+str(q[4])+'hs_'+\
					self.video.name.split('/')[-1].split('.')[0]
		npsave(nombre, self.dataClasif, allow_pickle=True)
		MsgBox = messagebox.showinfo('Guardar','Se guardaron los datos'+\
									' correctamente bajo el nombre: '+nombre,
									icon = 'warning')

	def saveDataAs(self):
		nombre = filedialog.asksaveasfilename(defaultextension='.npy',
												initialdir=self.dir)
		npsave(nombre, self.dataClasif, allow_pickle=True)

	def CargarDatos(self):
		dat = filedialog.askopenfile(mode='r',initialdir=self.dir,
										 title = "Seleccionar Archivo")
		try:
			aux = npload(dat,allow_pickle=True)
			self.dataClasif    = aux
			self.ActualPos     = aux[-1][0]
			self.contsConDatos = aux[-1][1]
		
		except:
			MsgBox = messagebox.showinfo('Cargar','No se pudo Cargar:'+dat,
									icon = 'warning')

	#--------------------------------------------------------------------------
	""" Cerrar Programa"""
	#--------------------------------------------------------------------------
	def _exit(self):
		""" Salir??"""
		MsgBox = messagebox.askquestion ('Salir','Querés cerrar '+\
										'la aplicación? \n Si no guardaste tus'+\
										' datos quedarán solo guardados en un '+
										'temporal que pisa al anterior.',
										icon = 'warning')
		if MsgBox == 'yes':
			self.destroy()
		else:
			pass
	#--------------------------------------------------------------------------

def main():
	#vid = VideoCapture('/home/ulises/00_Doctorado/rivas_06_may_19/analisisCampo/VideoTestGui/VidCam1_6_5_19222_conts2.avi')
	#conts = npload('/home/ulises/00_Doctorado/rivas_06_may_19/analisisCampo/VideoTestGui/VidCam1_6_5_19222_conts2.npy',allow_pickle=True)
#	gui=GUI(video=vid,contours=conts,listaDePlantas=listaMalezas)
	gui=GUI(listaDePlantas=listaMalezas,nombres=nombresAMostrar)
	gui.tk.mainloop()

