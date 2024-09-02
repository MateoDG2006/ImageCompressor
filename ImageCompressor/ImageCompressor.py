from PIL import Image
import os

def Proximity(res,Xaxis):
	lowest_index = 0
	if(Xaxis):
		resoluciones = [1920,2560,3840]
	else:
		resoluciones = [1080,1440,2160]

	lowest = abs(res-resoluciones[0])

	for resolu in resoluciones:
		prox = abs(res - resolu)
		if(lowest > prox):
			lowest = prox
			lowest_index = resoluciones.index(resolu)

	new_res = resoluciones[lowest_index]

	return new_res

folder = input("Ingrese la direccion del folder con imagenes: ")

output_folder = input("Ingrese la direccion del folder editados: ")

files = [f for f in os.listdir(folder)]

for file in files:
	input_file = os.path.join(folder,file)
	print(file)
	output_file = os.path.join(output_folder,file.replace(".jpg","-") +"compressed.jpg")
	ima = Image.open(input_file)
	width, height = ima.size
	res = width/height

	resolution_width = Proximity(width,True)
	resolution_height = Proximity(height,False)



	print(res)
	print(height)
	print(width)

	if res == 16/9:
		print("Resolucion optima");
		resize_image = ima.resize((resolution_width,resolution_height))
		resize_image.save()
	else:
		print("Resolucion incorrecta");
		if width < height:
			new_resolution = [int(resolution_height*res),resolution_height]
		else:
			new_resolution = [resolution_width,int(resolution_width/res)]

		resize_image = ima.resize(new_resolution)
		background_image = Image.new('RGB',(resolution_width,resolution_height),(225,225,225))
		posX = (resolution_width - new_resolution[0])/2
		posY = (resolution_height - new_resolution[1])/2
		background_image.paste(resize_image,(int(posX),int(posY)))
		background_image.save(output_file)	