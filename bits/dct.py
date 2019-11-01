import cv2
import numpy as np
import math
import qrcode
import os
from PIL import Image

def createCode(username, url):
	qr = qrcode.QRCode(     
		version=1,     
		error_correction=qrcode.constants.ERROR_CORRECT_L,     
		box_size=1,     
		border=4, 
	) 
	qr.add_data(username) 
	qr.make()  
	img = qr.make_image()
	print("url:"+url)
	print(os.path.abspath(url))
	img.save(url + '/code/code.png')
	print("img_size:{}".format(img.pixel_size))
	return img.pixel_size, img.pixel_size

def DCT(url, img):
	targetImageOrigin = cv2.imread(url + "/" + str(img))
	waterMark = cv2.imread(url +'/code/code.png')
	waterMarkNew = cv2.resize(waterMark,(waterMark.shape[0],waterMark.shape[1]))
	bsrc = cv2.bitwise_not(waterMarkNew)
	graysrc=cv2.cvtColor(waterMarkNew,cv2.COLOR_BGR2GRAY)  
	ret,bsrc = cv2.threshold(graysrc,70,255,1)  
	targetImage=cv2.cvtColor(targetImageOrigin,cv2.COLOR_RGB2YUV)  
	hostf=targetImage.astype('float32')
	c1 = np.size(hostf, 0)
	c2 = np.size(hostf, 1)
	rows = int(c1/8)
	cols = int(c2/8)
	# print(rows, cols)
	max_message = rows*cols

	w1 = np.size(bsrc, 0)
	w2 = np.size(bsrc, 1)
	# print(w1*w2, max_message)
	if w1*w2 > max_message:
		# print("No")
		return

	for i in range(bsrc.shape[0]):
		for j in range(bsrc.shape[1]):
			part8x8=cv2.dct(hostf[8*i:8*i+8,8*j:8*j+8,1])
			if bsrc[i][j] == 0:
				a = -1
			else:
				a = 1
			for ii in range(0,8):
				for jj in range(0,8):
					part8x8[ii][jj] = part8x8[ii][jj] * (1 + a*0.03)
			hostf[8*i:8*i+8,8*j:8*j+8,1] = cv2.idct(part8x8)
	hostf=cv2.cvtColor(hostf.astype('uint8'),cv2.COLOR_YUV2RGB) 
	cv2.imwrite(url + "/" + img, hostf)

def extract(sizex,sizey):
	originImage = cv2.imread("045.png")
	waterMarkImage = cv2.imread("save.png")
	originImage = cv2.cvtColor(originImage,cv2.COLOR_RGB2YUV)
	waterMarkImage = cv2.cvtColor(waterMarkImage,cv2.COLOR_RGB2YUV)
	originImage=originImage.astype('float32')
	waterMarkImage=waterMarkImage.astype('float32')
	code = [([0]*sizex) for i in range(sizey)]
	print(waterMarkImage.shape)
	for i in range(sizex):
		for j in range(sizey):
			water8x8=cv2.dct(waterMarkImage[8*i:8*i+8,8*j:8*j+8,1])
			origin8x8 = cv2.dct(originImage[8*i:8*i+8,8*j:8*j+8,1])
			if(water8x8[0][0] > 0):
				if water8x8[0][0] >= origin8x8[0][0]:
					code[i][j] = 255
				else:
					code[i][j] = 0
			else:
				if water8x8[0][0] >= origin8x8[0][0]:
					code[i][j] = 0
				else:
					code[i][j] = 255
	cv2.imwrite("decode.png", np.asarray(code))


def dctWaterMarking(url, username):
	#url = "./bits/images"
	code_path = url + "/code"
	print(os.path.abspath(url))
	if not(os.path.exists(code_path)):
		os.mkdir(code_path)
	if os.path.exists(os.path.join(url, "textures")):
		img_ls = [os.path.join("textures",i) for i in os.listdir(os.path.join(url,"textures")) if ((i.endswith('png') or i.endswith('jpeg') or i.endswith('jpg')) and not(i.startswith('preview')))]
	else:
		img_ls = [i for i in os.listdir(url) if ((i.endswith('png') or i.endswith('jpeg') or i.endswith('jpg')) and not(i.startswith('preview')))]
	print(img_ls)
	createCode(username, url)
	for img in img_ls:
		DCT(url, img)

