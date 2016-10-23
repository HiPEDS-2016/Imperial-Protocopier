//-------------------------------------------------------//
//       HiPEDS Group Project - Hardware Team            //
//              Imperial College London                  //
//-------------------------------------------------------//

// Last Modified 23 Oct 2016


#include<Servo.h>

//Program Constatnts
#define SERVO_STOP 1500
#define SERVO_MIN 1000
#define SERVO_MAX 2000
#define STEP 140

//Interface Pins
int SERVO_PIN=5;
int POT1_PIN=A0;
int POT2_PIN=A1;
int SWITCH_PIN=A3;

//Global Variables
int val1,val2,sw1;
int val1_n,val2_n,sw1_n;
int com_speed;

//Servo Class Instance
Servo servo;


//Function runs only one time, on power-up or reset
void setup() {
  
  //Attach Servo pin to Instance
  servo.attach(SERVO_PIN);

  //Establish a Serial Communication via USB with a computer (optional)
  Serial.begin(9600);

  //keep servo stoped for 1 sec after power up
  servo.writeMicroseconds(SERVO_STOP);
  delay(1000);
}

//Function runs repeatedly after setup() 
void loop() {

  //--------------------------------------------------------------
  //Read Potentiometers
  //--------------------------------------------------------------
  
    //Read Speed Pot
    val1 =analogRead(POT1_PIN);
    val1_n = map(val1,0,1023,200,500);
  
    //Read Pausing-time Pot
    val2 =analogRead(POT2_PIN);
    val2_n = map(val2,0,1023,0,1000);
  
    //Read Direction Switch
    sw1 =analogRead(SWITCH_PIN);
    if(sw1>=700){
      sw1_n=0;
      com_speed = SERVO_STOP-val1_n;
    }else{
      sw1_n=1;
      com_speed = SERVO_STOP+val1_n;
    }
  
    //Print values on computer (optional)
    Serial.println("Speed: "); Serial.println(val1_n);
    Serial.println("Pause: "); Serial.println(val2_n);
    //Serial.println("Direction: "); Serial.println(sw1_n);
    Serial.println("");
    
    //hardcoded test values
    //--------------------------------------
    //val1_n=170; //counter-clockwise
    //val1_n=240; //clockwise
    //val2_n=200; //clockwise
    //sw1_n=0;


  //--------------------------------------------------------------
  //Execute Movement
  //--------------------------------------------------------------

    //Rotate with commanded speed for predifined time
    //---------------------------------------------------
    
    if(com_speed >= SERVO_MIN && com_speed <= SERVO_MAX){
      servo.writeMicroseconds(com_speed);  //clockwise
    }else{
        if(com_speed > SERVO_MAX){
            servo.writeMicroseconds(SERVO_MAX);
        }else{
            servo.writeMicroseconds(SERVO_MIN); 
        }
    }
    delay(STEP);
  
   
    //Stand steal for predifined/controlled time
    //---------------------------------------------------
    servo.writeMicroseconds(SERVO_STOP);
    delay(val2_n);
  

  //Stop Servo
  //servo.writeMicroseconds(1500);
  //delay(20000);

}
