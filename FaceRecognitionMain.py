# -*- coding: utf-8 -*-

"""
Created on Fri Nov 15 19:17:54 2019

@author: Bo

Show user what computer see
"""

import face_recognition
import python_speech_features
import cv2
import numpy as np
import os
import time
import datetime
import win32com.client
import pyttsx3
import easygui as g
from tkinter import *

# Load image label and coding
known_face_encodings = []
known_face_names = []
image_label_path = "./image_label/"
for i in os.listdir(image_label_path):
	file_path = os.path.join(image_label_path,i)  # join path
	image_read = face_recognition.load_image_file(file_path)
	image_coding = face_recognition.face_encodings(image_read)[0]
	known_face_encodings.append(image_coding)
	known_face_names.append(str(i).split('.')[0])

# Initialize
speaker = pyttsx3.init()
# speaker = win32com.client.Dispatch("SAPI.SpVoice")

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

def sign_name(video_capture, frame, sign_path, name):
	# sign in part
	sign_storage = sign_path + "/" + name + ".jpg"
	cv2.imwrite(sign_storage, frame)
	speaker.say("你好")
	time.sleep(0.05)
	speaker.say("请问你是")
	speaker.say(name)
	speaker.say("吗？")
	speaker.runAndWait()
	# Name ensure
	choices = ["我是" + name,
				"我不是" + name + "，请重新识别",
				"我不是" + name + "，退出"
			]
	reply = g.buttonbox('打卡确认',choices=choices)

	if reply == "我是" + name:
		speaker.say("打卡成功")
		speaker.runAndWait()
	elif reply == "我不是" + name + "，请重新识别":
		speaker.say("重新识别中")
		speaker.runAndWait()
		face_detection_sign(video_capture, sign_path)
	elif reply == "我不是" + name + "，退出":
		speaker.say("好的")
		speaker.runAndWait()
		cv2.imshow('Video', "./default_show/White.jpg")
		time.sleep(2)

# add label to image
def display_result_sign(video_capture, frame, face_locations, face_names, sign_path):
	for (top, right, bottom, left), name in zip(face_locations, face_names):
		if name == "Unknown":
			nothing = True
		else:
			# Scale back up face locations since the frame we detected in was scaled to 1/4 size
			top *= 4
			right *= 4
			bottom *= 4
			left *= 4

			# Draw a box around the face
			cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

			# Draw a label with a name below the face
			cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
			font = cv2.FONT_HERSHEY_DUPLEX
			cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

			# sign name
			sign_name(video_capture, frame, sign_path, name)
			
	return frame

def face_detection_sign(video_capture, sign_path):
	
	# Initialize some variables
	face_locations = []
	face_encodings = []
	face_names = []
	process_this_frame = True
	
	while True:
		# Grab a single frame of video
		ret, frame = video_capture.read()
		# Resize frame of video to 1/4 size for faster face recognition processing
		small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
		# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
		rgb_small_frame = small_frame[:, :, ::-1]
	
		# Only process every other frame of video to save time
		if process_this_frame:
			# Find all the faces and face encodings in the current frame of video
			face_locations = face_recognition.face_locations(rgb_small_frame)
			face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
	
			face_names = []
			for face_encoding in face_encodings:
				# See if the face is a match for the known face(s)
				matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
				name = "Unknown"

				# If a match was found in known_face_encodings, just use the first one.
				# Store sign in image
				# if True in matches:
				# 	first_match_index = matches.index(True)
				# 	name = known_face_names[first_match_index]

				# Or instead, use the known face with the smallest distance to the new face
				face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
				best_match_index = np.argmin(face_distances)
				if matches[best_match_index]:
					name = known_face_names[best_match_index]
					face_names.append(name)

		process_this_frame = not process_this_frame

		if len(face_names) == 0:
			cv2.imshow('Video', frame)
			continue
		else:
			# Display the frame & sign
			frame = display_result_sign(video_capture, frame, face_locations, face_names, sign_path)
			cv2.imshow('Video', frame)

		# Hit 'q' on the keyboard to quit!
		# To Do: 退出拍照留名
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

def face_sign(sign_type, video_capture):
	# Get date
	date = datetime.date.today()

	# Sign path
	sign_in_path = "./sign/sign-in_" + str(date)
	sign_off_path = "./sign/sign-off_" + str(date)
	# Create path for sign pic storage
	if not os.path.exists(sign_in_path):
		os.mkdir(sign_in_path)
	if not os.path.exists(sign_off_path):
		os.mkdir(sign_off_path)

	sign_path = ""
	if sign_type == "sign_in":
		sign_path == sign_in_path
	elif sign_type == "sign_off":
		sign_path == sign_off_path

	# Recognize face and sign
	face_detection_sign(video_capture, sign_path)

# Main
while True:
	
	# Whether sign
	choices = ["上班打卡",
				"下班打卡"
			]
	reply = g.buttonbox('打卡选择',choices=choices)
	if reply == "上班打卡":
		face_sign("sign_in", video_capture)
	elif reply == "下班打卡":
		face_sign("sign_off", video_capture)

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()