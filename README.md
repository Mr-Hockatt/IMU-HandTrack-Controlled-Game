# IMU-HandTrack-Controlled-Game
Python game controlled by and Arduino-based IMU system and handtracking via openCV and Mediapipe.
This project was created as part of my <b>Digital Signal Processing</b> class on my 7th semester of Mechatronics Engineering.

![gui](https://user-images.githubusercontent.com/53312754/120088795-e649a180-c0b9-11eb-98be-0b633f35de2f.png)

##Features
<ul>
  <li>Pygame-based platformer</li>
  <li>HandTracking via <a href="https://google.github.io/mediapipe/solutions/hands">Mediapipe Hands</a> library</li>
  <li>Movement detection via IMU-based system on Arduino</li>
</ul>

The movement of the character is controlled by both systems (a combination of both) basically <a href="https://en.wikipedia.org/wiki/Aircraft_principal_axes">pitch and roll</a> is used to control it so that pitch makes the character jump and roll makes it go right (clockwise turn) or left (anti-clockwise turn).

![movements](https://user-images.githubusercontent.com/53312754/120088869-96b7a580-c0ba-11eb-9398-9e1c2b3482e2.png)
