from turtle import back
from PIL import Image
import os

resolucionesX = [1920,2560,3840]
resolucionesY = [1080,1440,2160]

CanvasColor = (239,239,239)
def ImageInfo(res,orWidth,orHeight,newWidth,newHeight,CanvasWidthSize,CanvasHeightSize):
	print(f"Resolution: {res}\n Dimension Original: {orWidth}x{orHeight} \n Dimension Comprimida: {newWidth}x{newHeight} \n Dimension Canvas: {CanvasWidthSize}x{CanvasHeightSize}\n")

def DetermineResolutionByIndex(res,Xaxis):
	lowest_index = 0
	if(Xaxis):
		resoluciones = resolucionesX
	else:
		resoluciones = resolucionesY

	lowest = abs(res-resoluciones[0])

	for resolu in resoluciones:
		prox = abs(res - resolu)
		if(lowest > prox):
			lowest = prox
			lowest_index = resoluciones.index(resolu)

	return lowest_index

def ImageCompressor():
	folder = input("Ingrese la direccion del folder con imagenes: ")

	output_folder = input("Ingrese la direccion del folder editados: ")

	files = [f for f in os.listdir(folder)]

	for file in files:
		input_file = os.path.join(folder,file)
		
		print(f"\nNombre: {file}")

		output_file = os.path.join(output_folder,"Comp_" + file + ".jpg")
		ima = Image.open(input_file)

		width, height = ima.size
	
		res = width/height
		indexforWidthCanvas = DetermineResolutionByIndex(width,True)
		indexforHeightCanvas = DetermineResolutionByIndex(height,False)

		CanvasWidthResolution = resolucionesX[indexforWidthCanvas]
		CanvasHeightResolution = resolucionesY[indexforHeightCanvas]

		resize_width = CanvasWidthResolution
		resize_height = CanvasHeightResolution

		if res != 16/9:
			print("AGREGANDO BORDES \n")
			

			if width > height: #La imagen es mas ANCHA que alta o esta en PANORAMICA
				CanvasHeightResolution = resolucionesY[indexforWidthCanvas]
				resize_width = CanvasWidthResolution
				resize_height = resize_width/res
				if resize_height > CanvasHeightResolution: #ACA COMPARO SI LA IMAGEN ENCAJA EN EL CANVAS
					print("***CAMBIO POR ALTURA***\n")
					resize_height = CanvasHeightResolution
					resize_width = resize_height * res
			else: #La imagen es mas ALTA que ancha o esta en VERTICAL
				CanvasWidthResolution = resolucionesX[indexforHeightCanvas]
				resize_height =CanvasHeightResolution
				resize_width = resize_height * res

			resizeImageXPos_inCanvas = abs((resize_width-CanvasWidthResolution))/2
			resizeImageYPos_inCanvas = abs((resize_height-CanvasHeightResolution))/2

			resize_image = ima.resize((int(resize_width),int(resize_height)))
			backgroundImage = Image.new('RGB',(CanvasWidthResolution,CanvasHeightResolution),CanvasColor)

			ImageInfo(res,width,height,resize_width,resize_height,CanvasWidthResolution,CanvasHeightResolution)

			backgroundImage.paste(resize_image,(int(resizeImageXPos_inCanvas),int(resizeImageYPos_inCanvas)))
		
			backgroundImage.save(output_file)
		else:
			print("COMPRESION DIRECTA \n")
			ImageInfo(res,width,height,resize_width,resize_height,CanvasWidthResolution,CanvasHeightResolution)
			resize_image = ima.resize((resize_width,resize_height))
			backgroundImage = Image.new('RGB',(CanvasWidthResolution,CanvasHeightResolution),CanvasColor)
			backgroundImage.paste(resize_image,(0,0))
			backgroundImage.save(output_file)
		print("TERMINADO...\n\n\n")

while True:
	ImageCompressor()
