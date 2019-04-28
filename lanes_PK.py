# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 21:38:46 2019

@author: pruthvi
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

def make_coordinates(image,line_parameters): 
	slope, intercept = line_parameters
	y_start = image.shape[0]   # shape = [vertical pixel, width pixel, colour channel]
	y_end  = int((3/5)*y_start) 

	x_start = int( (y_start-intercept)/ slope )    #y = mx+b    x = (y-b)/m
	x_end = int( (y_end-intercept) / slope )

	return np.array( [x_start,y_start,x_end,y_end] )


def average_slope_intersect(image, lines):
	left_fit = []  #contain coordinates of the averaged lines on the left
	right_fit = [] #contain coordinates of the avergaed line on the right
	for line in lines:
		x1,y1,x2,y2 = line.reshape(4)  #point (x1,y1) and (x2,y2) to connect and form line
		parameters = np.polyfit( (x1,x2), (y1,y2) , 1) #3rd argument refers to degree of poly function
		slope = parameters[0]
		intercept = parameters[1]

		if slope < 0:
			left_fit.append((slope,intercept))
		else:
			right_fit.append((slope,intercept))

	left_fit_avg = np.average(left_fit,axis = 0) #axis = 0 means that we 
												#take average vertically along the rows to get the average slope and average y intercept
	right_fit_avg = np.average(right_fit,axis = 0)
	left_line = make_coordinates(image,left_fit_avg)
	right_line = make_coordinates(image,right_fit_avg)

	return np.array( [left_line,right_line] )
	
	# print(left_fit)
	# print(right_fit)



def canny(image):
	gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
	blur = cv2.GaussianBlur(gray,(5,5),0) #5x5 kernal and deviation = 0 
	canny = cv2.Canny(blur,50,150)
	return canny

def region_of_interest(image):
	height = image.shape[0] #correspond to number of row
	polygons = np.array([
	[(200,height),(1100,height),(550,250)]
	])  #create a triangle

	#then apply the triangle to the black mask, however to note that we only create one ploygon, hence we need to specify it in an array
	mask = np.zeros_like(image)  #fill the mask with all black, intensity = 0
	cv2.fillPoly(mask,polygons,255) #take a triangle which borudaries being defined, apply to a mask such that the area bounded by the polygonal contour will be completely white
	masked_image = cv2.bitwise_and(image,mask) #comment as in step 6
	return masked_image

def display_lines(image,lines):   #lines is a 3d array [ [ [] ] ]
	line_image = np.zeros_like(image)

	if lines is not None:
		for line in lines:
			x1,y1,x2,y2 = line  #reshape it into a 1D array, but instead we spread into 4 variables
			cv2.line(line_image, (x1,y1), (x2,y2),(255,0,0), 10)  #4th argument = blue colour, 5th - line thickness
	return line_image

# def display_lines(image,lines):   #lines is a 3d array [ [ [] ] ]
# 	line_image = np.zeros_like(image)

# 	if lines is not None:
# 		for line in lines:
# 			x1,y1,x2,y2 = line.reshape(4)  #reshape it into a 1D array, but instead we spread into 4 variables
# 			cv2.line(line_image, (x1,y1), (x2,y2),(255,0,0), 10)  #4th argument = blue colour, 5th - line thickness
# 	return line_image

#----------------------------- image ---------------------------------------
# image = cv2.imread('test_image_1.jpg')
# lane_image = np.copy(image) #we create a copy so that any changes made on the copy wont be reflected in the original mutable array
# canny_image = canny(lane_image)
# cropped_image = region_of_interest(canny_image)
# lines =  cv2.HoughLinesP(cropped_image,2, np.pi/180, 100, np.array([]), minLineLength = 40, maxLineGap=5)  #2 (pixel) & 3rd argument are the resolution og the HOugh accumulator array, 4th is threshold *see step 8
# 													#other arguments pls refer to step 8
# 											#we specify 2 pixels and 1 degree which need to convert to rad, we can check using 20 pixels to see the different
# average_lines = average_slope_intersect(lane_image, lines)
# lines_image = display_lines(lane_image,average_lines)
# combo_image = cv2.addWeighted(lane_image, 0.8, lines_image, 1, 1)
											
# # plt.imshow(combo_image)
# # plt.show()
# cv2.imshow('result',combo_image)
# cv2.waitKey(0)  #display the image until we press anything


#------------------------- video ---------------------------------------------
cap = cv2.VideoCapture('Video_for_test.mp4')
while (cap.isOpened()):
	_,frame = cap.read()
	canny_frame = canny(frame)
	cropped_frame = region_of_interest(canny_frame)
	lines = cv2.HoughLinesP(cropped_frame,2,np.pi/180,100,np.array([]),minLineLength = 40, maxLineGap = 5)
	average_lines = average_slope_intersect(frame,lines)
	lines_frame = display_lines(frame,average_lines)
	combo_frame = cv2.addWeighted(frame,0.8,lines_frame,1,1)

	cv2.imshow('Video',combo_frame)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()


