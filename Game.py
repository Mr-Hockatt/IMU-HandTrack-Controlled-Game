import pygame
import serial
import time
from pygame.locals import *
from pygame import mixer


import numpy as np
import cv2
import mediapipe as mp




serial_port = serial.Serial('COM3', 9600)

def get_offsets():
	
	pitch = list()
	roll = list()

	while len(pitch) < 500:
		
		while serial_port.inWaiting() == 0:
			pass
		
		data = serial_port.readline()

		if len(data) > 1:

			data = data.decode()
			if len(data.split(",")) == 2:
				pitch_measurement, roll_measurement = data.split(",")

				pitch.append(float(pitch_measurement))
				roll.append(float(roll_measurement))

	pitch_offset = sum(pitch) / len(pitch)
	roll_offset = sum(roll) / len(roll)


	return (pitch_offset, roll_offset)


print("Encontrando offsets, Wait...")
pitch_offset, roll_offset = get_offsets()

print(f"pitch offset: {pitch_offset}")
print(f"roll offset: {roll_offset}")





pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 30

screen_width = 500
screen_height = 500

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')


#define font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)

#define game variables
tile_size = 25
game_over = 0
main_menu = True
score = 0

#define colours
white = (255, 255, 255)
blue = (0, 0, 255)
red = (255, 0, 0)


#load images
bg_img = pygame.image.load('img/bgrb.png')
restart_img = pygame.image.load('img/restart.png')
start_img = pygame.image.load('img/start.png')
exit_img = pygame.image.load('img/exit.png')


#load sounds
coin_fx = pygame.mixer.Sound('img/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)
restart_fx = pygame.mixer.Sound('img/restart.wav')
restart_fx.set_volume(0.5)


def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		#draw button
		screen.blit(self.image, self.rect)

		return action


class Player():
		
	def __init__(self, x, y):
		self.reset(x, y)
		

	def reset(self, x, y):

		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'img/guy{num}.png')
			img_right = pygame.transform.scale(img_right, (25, 50))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load('img/ghost.png')
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True


	def update(self, game_over, pitch, roll):
		dx = 0
		dy = 0
		walk_cooldown = 5



		if game_over == 0:
			#get keypresses
			key = pygame.key.get_pressed()

			if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
				jump_fx.play()
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_SPACE] == False:
				self.jumped = False
			if key[pygame.K_LEFT]:
				dx -= 5
				self.counter += 1
				self.direction = -1
			if key[pygame.K_RIGHT]:
				dx += 5
				self.counter += 1
				self.direction = 1
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]

			if pitch > 15 and self.jumped == False and self.in_air == False:
				jump_fx.play()
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_SPACE] == False:
				self.jumped = False
			if roll < -30:
				dx -= 5
				self.counter += 1
				self.direction = -1
			if roll > 30:
				dx += 5
				self.counter += 1
				self.direction = 1
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#handle animation

			if self.counter > walk_cooldown:
				self.counter = 0	
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]



			#add gravity

			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y


			#check for collision
			self.in_air = True
			for tile in world.tile_list:
				#check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#check if above the ground i.e. falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False

			#check for collision with enemies
			if pygame.sprite.spritecollide(self, blob_group, False):
				game_over = -1
				game_over_fx.play()

			#check for collision with lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1
				game_over_fx.play()

		
			#update player coordinates

			self.rect.x += dx
			self.rect.y += dy


		elif (game_over == -1):
			self.image = self.dead_image
			draw_text('GAME OVER!', font, red, 70, 60)
			if self.rect.y > 10:
				self.rect.y -= 5


		#draw player onto screen
		screen.blit(self.image, self.rect)
		#pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
	
		return game_over

def draw_grid():
	for line in range(0, 20):
		pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
		pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))



class World():

	def __init__(self, data):
		self.tile_list = []

		#load images

		dirt_img = pygame.image.load('img/dirt.png')
		grass_img = pygame.image.load('img/dirt.png')

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 3:
					blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
					blob_group.add(blob)
				if tile == 6:
					lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					lava_group.add(lava)
				if tile == 7:
					coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					coin_group.add(coin)

				col_count += 1
			row_count += 1

	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])
			#pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/blob.png')
		self.rect = self.image.get_rect()
		self.rect.x = x-20
		self.rect.y = y-10
		self.move_direction = 1
		self.move_counter = 0

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 35:
			self.move_direction *= -1
			self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/lava.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

class Coin(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/coin.png')
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)



world_data = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0], 
[0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0], 
[0, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 0], 
[0, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 2, 2, 2, 4, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 2, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2], 
[0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], 
[0, 0, 0, 0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], 
[0, 0, 0, 0, 2, 1, 1, 1, 1, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1], 
[1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]



player= Player(50, 380)

blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

#create dummy coin for showing the score
score_coin = Coin(25, 25)
coin_group.add(score_coin)

world= World(world_data)


#buttons
restart_button = Button(250, 220, restart_img)
start_button = Button(175, 200, start_img)
exit_button = Button(410, 20, exit_img)

run = True





"""
DEFINICION E INICIALIZACION CAMARA
"""
t_0 = time.time()

video_capture = cv2.VideoCapture(0)
mphands = mp.solutions.hands
hands = mphands.Hands()
mpdraw = mp.solutions.drawing_utils

previous_time = 0
current_time = 0


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



pitch_arduino = 0
roll_arduino = 0
pitch_camara = 0
roll_camara = 0


while run:

	#clock.tick(fps)
	screen.blit(bg_img, (0, 0))
	

	"""
	SECCION ADQUISICION pitch + roll POR ARDUINO
	"""
	while serial_port.inWaiting() == 0:
		pass
	data = serial_port.readline()

	if len(data) > 1:

		data = data.decode()

		if len(data.split(",")) == 2:
		
			pitch_arduino, roll_arduino = data.split(",")
		
			pitch_arduino = float(pitch_arduino) - pitch_offset
			roll_arduino = float(roll_arduino) - roll_offset

			print(f"{pitch_arduino}         {roll_arduino}")
	
	"""
	SECCION ADQUISICION pitch + roll POR CAMARA
	"""
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

			roll_camara = inclination_angle

			cv2.putText(image, str(inclination_angle), (150, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

			pitch_camara = wrist[1]

			if wrist[1] < 0.5:

				pitch_camara = 20
				cv2.putText(image, "JUMP!", (500, 300), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

			draw_normal_vector(image, wrist, normalized_normal_vector + wrist)

			mpdraw.draw_landmarks(image, hand_landmarks, mphands.HAND_CONNECTIONS)


	current_time = time.time()
	fps = 1 / (current_time - previous_time)
	previous_time = current_time

	cv2.putText(image, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)


	cv2.imshow("Camera", image)
	cv2.waitKey(1)

	"""
	SECCION UNIFICACION SEÑAL pitch + roll
	"""
	
	pitch = pitch_arduino * (0.5) + pitch_camara * (0.5)
	roll = roll_arduino * (0.5) + roll_camara * (0.5)


	"""
	SECCION DEL JUEGO Y UPDATE
	"""

	if main_menu == True:
		if exit_button.draw():
			run = False
		if start_button.draw():
			main_menu = False
	else:
		world.draw()
		blob_group.draw(screen)
		lava_group.draw(screen)
		coin_group.draw(screen)
		game_over = player.update(game_over, pitch, roll)

	if game_over == 0:
		blob_group.update()
		if pygame.sprite.spritecollide(player, coin_group, True):
				score += 1
				coin_fx.play()
		draw_text( str(score), font_score, white, 35, 10)

	
	if game_over == -1:
			if restart_button.draw():
				player.reset(50, 380)
				game_over = 0
				score = 0
				restart_fx.play()


	#draw_grid()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()