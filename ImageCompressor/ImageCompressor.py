from PIL import Image
import sys
from multiprocessing import Process, Pool
import subprocess
import os
import json

with open("config/defaultConfig.json", "r", encoding="utf-8") as f:
    config = json.load(f)

resolucionesX = config["resolucionesX"]
resolucionesY = config["resolucionesY"]

Image.MAX_IMAGE_PIXELS = 933120000

fileIMGTypes = config["fileIMGTypes"]

fileVIDTypes = config["fileVIDTypes"]

CanvasColor = tuple(config["CanvasColor"])

video_poolArray = {
	"paths": [],
	"screenshots": [],
	"reverse": []
	}

class ImageFile:
	def __init__(self, file,folder,output_folder):
		self.path = file.path
		
		self.name = os.path.basename(file.path)
		self.extension = os.path.splitext(self.name)[1].lower()
		self.folder = folder
		self.output_folder = output_folder
		
		self.imageFile = Image.open(self.path)
		self.resolution = res = self.imageFile.size[0]/self.imageFile.size[1]
		self.CanvasWidth = int(self.DetermineCanvasResolution(self.imageFile.size)[0])
		self.CanvasHeight = int(self.DetermineCanvasResolution(self.imageFile.size)[1])
		self.ResizeImageWidth = int(self.DetermineImageResize()[0])
		self.ResizeImageHeight = int(self.DetermineImageResize()[1])
	
	def __str__(self):
		return f"File: {self.name}, Resolution: {self.resolution}, Canvas: {self.CanvasWidth}x{self.CanvasHeight}, Resize: {self.ResizeImageWidth}x{self.ResizeImageHeight}"

	def DetermineCanvasResolution(self,dimensions):	
		distanceY = 0

		imageSizeX = dimensions[0]
		imageSizeY = dimensions[1]

		min_distanceX = imageSizeX - resolucionesX[0]
		min_distanceY = imageSizeY - resolucionesY[0]
		min_sizeX = resolucionesX[0]
		min_sizeY = resolucionesY[0]
		

		for resolution in resolucionesX:
			distance = abs(imageSizeX - resolution)
			if(min_distanceX > distance):
				min_distanceX = distance
				min_sizeX = resolution

		for resolution in resolucionesY:
			distance = abs(imageSizeY - resolution)
			if(min_distanceY > distance):
				min_distanceY = distance
				min_sizeY = resolution

		if min_distanceX < min_distanceY:
			min_sizeY = resolucionesY[resolucionesX.index(min_sizeX)]
		elif min_distanceY < min_distanceX:
			min_sizeX = resolucionesX[resolucionesY.index(min_sizeY)]
		elif min_distanceX == min_distanceY:
			if imageSizeX > imageSizeY:
				min_sizeX = imageSizeX
				min_sizeY = resolucionesY[resolucionesX.index(min_sizeX)]
			else:
				min_sizeY = imageSizeY
				min_sizeX = resolucionesX[resolucionesY.index(min_sizeY)]
		return (min_sizeX,min_sizeY)

	def DetermineImageResize(self):
		if self.resolution != 16/9:
			if self.imageFile.size[0] > self.imageFile.size[1]: #La imagen es mas ANCHA que alta o esta en PANORAMICA
				resize_width = self.CanvasWidth
				resize_height = resize_width/self.resolution
				if resize_height > self.CanvasHeight: #ACA COMPARO SI LA IMAGEN ENCAJA EN EL CANVAS
					resize_height = self.CanvasHeight
					resize_width = resize_height * self.resolution
			else: #La imagen es mas ALTA que ancha o esta en VERTICAL
				resize_height =self.CanvasHeight
				resize_width = resize_height * self.resolution
		else:
			resize_width = self.CanvasWidth
			resize_height = self.CanvasHeight

		return (resize_width,resize_height)              

class VideoFile:
	def __init__(self, file, folder, output_folder):
		self.path = file.path
		self.name = os.path.basename(file.path)
		self.extension = os.path.splitext(self.name)[1].lower()
		self.folder = folder
		self.output_folder = output_folder
		self.reverse = False
		self.screenshots = False


	def __str__(self):
		return f"Video File: {self.name}, Folder: {self.folder}, Output Folder: {self.output_folder}"

def ImageCompressor(input_file):
		
	print(input_file)

	output_file = os.path.join(input_file.output_folder, f"Comp_{input_file.name}.jpg")
	
	resize_image = input_file.imageFile.resize((input_file.ResizeImageWidth,input_file.ResizeImageHeight))
	
	XPos = int(abs((input_file.ResizeImageWidth-input_file.CanvasWidth))/2)
	YPos = int(abs((input_file.ResizeImageHeight-input_file.CanvasHeight))/2)

	backgroundImage = Image.new('RGB',(input_file.CanvasWidth,input_file.CanvasHeight),CanvasColor)
	backgroundImage.paste(resize_image,(XPos,YPos))
	backgroundImage.save(output_file)
	
	print("TERMINADO...\n\n\n")



def ScannerFolder(folder):
	has_html = any(
        os.path.isfile(os.path.join(folder, entry.name)) and entry.name.lower().endswith(".html")
        for entry in os.scandir(folder)
    )
	if has_html:
		print(f"Carpeta '{folder}' descartada por contener HTML (Posible Tour360)")
		return

	with os.scandir(folder) as folders:
		for file in folders:
			input_file_name = os.path.basename(file.name)
			if file.is_dir():
				ScannerFolder(file.path)

			elif input_file_name.startswith("Comp_"):
				print(f"Saltando ya comprimido: {input_file_name}")
				continue
			else:
				output_folder = os.path.join(folder, "EDITADOS")
				
				if not os.path.exists(output_folder):
					os.makedirs(output_folder)
				
				split_file = os.path.splitext(file)[1].lower()
				
				if split_file in fileIMGTypes:
					print("Imagen...")
					input_file = ImageFile(file,folder,output_folder)
					ImageCompressor(input_file)

				elif split_file in fileVIDTypes:
					print("Video...")
					input_file = VideoFile(file,folder,output_folder)
					option = input(f'Desea agregar el video {input_file.name} a la cola de procesamiento y/n:')
					if(option == 'y' or option == 'Y'):
						print("Agregando video a la cola...")
						option = input(f'Desea tomar primer y ultimo frame? y/n:')
						if(option == 'y' or option == 'Y'):
							input_file.screenshots = True
						option = input(f'Desea hacer video en reversa? y/n:')
						if(option == 'y' or option == 'Y'):
							input_file.reverse = True
						video_poolArray["paths"].append(input_file.path)
						video_poolArray["screenshots"].append(input_file.screenshots)
						video_poolArray["reverse"].append(input_file.reverse)
				else:
					continue
	
while True:
	folder = input("Ingrese la direccion del folder con imagenes: ")

	ScannerFolder(folder)
	if video_poolArray:
		print("Procesando videos...")
		script_path = os.path.abspath("VideoCompressor.py")

		# Abre una nueva terminal y ejecuta el script
		subprocess.Popen(
			f'start cmd /k python "{script_path}" "{video_poolArray}"',
			shell=True
		)		
