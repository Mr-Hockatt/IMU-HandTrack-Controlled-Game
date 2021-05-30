#include "I2Cdev.h"
#include "MPU6050.h"

// Arduino Wire library is required if I2Cdev I2CDEV_ARDUINO_WIRE implementation
// is used in I2Cdev.h
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif

// class default I2C address is 0x68
// specific I2C addresses may be passed as a parameter here
// AD0 low = 0x68 (default for InvenSense evaluation board)
// AD0 high = 0x69
MPU6050 accelgyro;
//MPU6050 accelgyro(0x69); // <-- use for AD0 high

int16_t ax, ay, az;
int16_t gx, gy, gz;
int16_t mx, my, mz;

float previous_t, current_t, delta_t;
float gyrox, gyroy, gyroz;



// uncomment "OUTPUT_READABLE_ACCELGYRO" if you want to see a tab-separated
// list of the accel X/Y/Z and then gyro X/Y/Z values in decimal. Easy to read,
// not so easy to parse, and slow(er) over UART.
#define OUTPUT_READABLE_ACCELGYRO

// uncomment "OUTPUT_BINARY_ACCELGYRO" to send all 6 axes of data as 16-bit
// binary, one right after the other. This is very fast (as fast as possible
// without compression or data loss), and easy to parse, but impossible to read
// for a human.
//#define OUTPUT_BINARY_ACCELGYRO


#define LED_PIN 13
bool blinkState = false;


void setup() {
    // join I2C bus (I2Cdev library doesn't do this automatically)
    #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
    #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
        Fastwire::setup(400, true);
    #endif

    // initialize serial communication
    // (38400 chosen because it works as well at 8MHz as it does at 16MHz, but
    // it's really up to you depending on your project)
    Serial.begin(9600);

    // initialize device
    //Serial.println("Initializing I2C devices...");
    accelgyro.initialize();

    // verify connection
    //Serial.println("Testing device connections...");
    //Serial.println(accelgyro.testConnection() ? "MPU6050 connection successful" : "MPU6050 connection failed");

    // use the code below to change accel/gyro offset values
    /*
    Serial.println("Updating internal sensor offsets...");
    // -76  -2359 1688  0 0 0
    Serial.print(accelgyro.getXAccelOffset()); Serial.print("\t"); // -76
    Serial.print(accelgyro.getYAccelOffset()); Serial.print("\t"); // -2359
    Serial.print(accelgyro.getZAccelOffset()); Serial.print("\t"); // 1688
    Serial.print(accelgyro.getXGyroOffset()); Serial.print("\t"); // 0
    Serial.print(accelgyro.getYGyroOffset()); Serial.print("\t"); // 0
    Serial.print(accelgyro.getZGyroOffset()); Serial.print("\t"); // 0
    Serial.print("\n");
    accelgyro.setXGyroOffset(-7099);
    accelgyro.setYGyroOffset(4927);
    accelgyro.setZGyroOffset(9927);
    accelgyro.setXAccelOffset(73);
    accelgyro.setYAccelOffset(-13);
    accelgyro.setZAccelOffset(17);
    Serial.print(accelgyro.getXAccelOffset()); Serial.print("\t"); // -76
    Serial.print(accelgyro.getYAccelOffset()); Serial.print("\t"); // -2359
    Serial.print(accelgyro.getZAccelOffset()); Serial.print("\t"); // 1688
    Serial.print(accelgyro.getXGyroOffset()); Serial.print("\t"); // 0
    Serial.print(accelgyro.getYGyroOffset()); Serial.print("\t"); // 0
    Serial.print(accelgyro.getZGyroOffset()); Serial.print("\t"); // 0
    Serial.print("\n");

    delay(8000);
    */
    // configure Arduino LED pin for output
    pinMode(LED_PIN, OUTPUT);

}

void loop() {
    // read raw accel/gyro measurements from device
    accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
    //accelgyro.getMotion9(&ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz);
    
        previous_t = current_t;        // Previous time is stored before the actual time read
        current_t = millis();            // Current time actual time read
        delta_t = (current_t - previous_t) / 1000;
        

        gyrox = gyrox + gx/131.0 * delta_t;
        gyroy = gyroy + gy/131.0 * delta_t;

        
        float phi = 180 * atan2(ay / 16384.0, az / 16384.0) / PI;
        float theta = 180 * atan2(-ax / 16384.0, sqrt(pow(ay / 16384.0, 2) + pow(az / 16384.0, 2))) / PI;
        //float phi = 180 * atan2(-ax / 16384.0, sqrt(pow(ay / 16384.0, 2) + pow(az / 16384.0, 2))) / PI;
        //float signz;
        //if (az > 0){signz = 1;}
        //else {signz = -1;}
        //float theta = 180 * atan2(ay / 16384.0, signz * sqrt(pow(ay / 16384.0, 2) + pow(az / 16384.0, 2))) / PI;

        //float roll = 0.04 * gyrox + 0.96 * phi;
        //float pitch = 0.04 * gyroy + 0.96 * theta;
        //float yaw = yaw + gz /131.0* delta_t;

        //Serial.println(String(roll) + "," + String(pitch) + "," + String(yaw));
        Serial.println(String(phi) + "," + String(theta));
        //Serial.println(String(ax) + " " + String(ay) + " " + String(az) + " " + String(gx) + " " + String(gy) + " " + String(gz) + " " + String(mx) + " " + String(my) + " " + String(mz));
        delay(50);
    

    // blink LED to indicate activity
    blinkState = !blinkState;
    digitalWrite(LED_PIN, blinkState);

}
