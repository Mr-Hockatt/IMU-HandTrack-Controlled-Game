# IMU-HandTrack-Controlled-Game
Python game controlled by and Arduino-based IMU system and handtracking via openCV and Mediapipe.</br>
This project was created as part of my <b>Digital Signal Processing</b> class on my 7th semester of Mechatronics Engineering.

![gui](https://user-images.githubusercontent.com/53312754/120088795-e649a180-c0b9-11eb-98be-0b633f35de2f.png)

## Features
<ul>
  <li>Pygame-based platformer</li>
  <li>HandTracking via <a href="https://google.github.io/mediapipe/solutions/hands">Mediapipe Hands</a> library</li>
  <li>Movement detection via <a href="https://en.wikipedia.org/wiki/Inertial_measurement_unit">IMU</a>-based system on Arduino</li>
</ul>

The movement of the character is controlled by both systems (a combination of both) basically <a href="https://en.wikipedia.org/wiki/Aircraft_principal_axes">pitch and roll</a> is used to control it so that pitch makes the character jump and roll makes it go right (clockwise turn) or left (anti-clockwise turn).

![movements](https://user-images.githubusercontent.com/53312754/120088869-96b7a580-c0ba-11eb-9398-9e1c2b3482e2.png)

## General explanation. How the Handtracking works?
The hand recognition and tracking happens thanks to mediapipe library. Basically, it returns the spacial relative coordinates of the 21 landmarks that the neural network detects. Once it happens, we take 3 points on the palm: landmarks 0 (nearest point to the wrist), 5 (index finger phalanx) and 17 (pinky finger phalanx) to create a plane and a orthogonal vector to it. Based on the angle that the vector creates between the vertical axis we measure the roll angle.</br>
For the pitch we just focused on the vertical position of the hand on the screen: If it is below the 50% of the screen then character does not jump, otherwise it does.</br>

![hand_landmarks](https://user-images.githubusercontent.com/53312754/120089110-d67f8c80-c0bc-11eb-8fff-2bc0d9cae90b.png)


## General explanation. How the IMU system works?
The IMU system detects angular velocities, which are then used to compute the pitch and roll of the sensor. Once computed, they are sent through serial port to the python program in order to send the signal to the character.

![imu](https://user-images.githubusercontent.com/53312754/120089158-3ece6e00-c0bd-11eb-931e-cb53583260c8.png)


## How to use it?
