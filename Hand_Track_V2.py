import numpy as np
import cv2
import mediapipe as mp
import time
import matplotlib.pyplot as plotter
import csv

t_0 = time.time()

video_capture = cv2.VideoCapture(0)
mphands = mp.solutions.hands
hands = mphands.Hands()
mpdraw = mp.solutions.drawing_utils

previous_time = 0
current_time = 0

wx = []
wy = []
wz = []

	

def find_normal_vector(v1, v2):
    
    normal_vector = np.cross(v1, v2)
    return normal_vector


def get_inclination_angle(vector, axis_vector):

	dot_product = np.dot(vector, axis_vector)
	magnitude_product = np.linalg.norm(vector) * np.linalg.norm(axis_vector)

	theta = np.arccos(dot_product / magnitude_product)

	return theta

def draw_normal_vector(image, initial_point, final_point):

	width, height, channels = image.shape

	frame_size = np.array([width, height])

	P0 = initial_point[:2] * frame_size
	P1 = final_point[:2] * frame_size

	P0 = np.array([int(p) for p in P0])
	P1 = np.array([int(p) for p in P1])

	cv2.line(image, P0, P1, (255, 0, 255), 15)



while (time.time() - t_0) < 30:

	success, image = video_capture.read()
	RGB_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	results = hands.process(RGB_image)

	
	if results.multi_hand_landmarks:
		for hand_landmarks in results.multi_hand_landmarks:
			
			wrist = hand_landmarks.landmark[0]
			index_finger = hand_landmarks.landmark[5]
			pinky = hand_landmarks.landmark[17]

			wrist = np.array([wrist.x, wrist.y, wrist.z])
			index_finger = np.array([index_finger.x, index_finger.y, index_finger.z])
			pinky = np.array([pinky.x, pinky.y, pinky.z])


			v1 = index_finger - wrist
			v2 = pinky - wrist

			normal_vector = find_normal_vector(v1, v2)
			normalized_normal_vector = normal_vector / np.linalg.norm(normal_vector)

			

			P0 = wrist[:2]
			P1 = normalized_normal_vector[:2] + wrist[:2]

			inclination_angle = np.arctan((P1 - P0)[0] / (P1 - P0)[1]) * 180 / np.pi

			cv2.putText(image, str(inclination_angle), (150, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

			if wrist[1] < 0.5:
				cv2.putText(image, "JUMP!", (500, 300), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

			draw_normal_vector(image, wrist, normalized_normal_vector + wrist)


			"""
			for id, landmark in enumerate(hand_landmarks.landmark):
				
				print(id, landmark)
				if id == 0:
					wx.append(landmark.x)
					wy.append(landmark.y)
					wz.append(landmark.z)

				#width, height, channels = image.shape

				#x, y = int(landmark.x * width), int(landmark.y*height)

				#print(id, x, y)
			"""
			mpdraw.draw_landmarks(image, hand_landmarks, mphands.HAND_CONNECTIONS)

	current_time = time.time()
	fps = 1 / (current_time - previous_time)
	previous_time = current_time

	cv2.putText(image, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)


	cv2.imshow("Camera", image)
	cv2.waitKey(1)



"""
plotter.plot([i for i in range(len(wx))], wx, label="x")
plotter.plot([i for i in range(len(wy))], wy, label="y")
plotter.plot([i for i in range(len(wz))], wz, label="z")
plotter.legend()
plotter.show()


with open("mapeo.csv", 'w') as file:

	writer = csv.writer(file)

	for x, y, z in zip(wx, wy, wz):
		row = [x, y, z]
		writer.writerow(row)
"""