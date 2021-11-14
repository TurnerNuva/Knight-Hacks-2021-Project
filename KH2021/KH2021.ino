#include <Arduino.h>
#include <U8x8lib.h>
#include <string.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif

U8X8_SSD1306_128X64_NONAME_4W_SW_SPI u8x8(/* clock=*/ 13, /* data=*/ 11, /* cs=*/ 10, /* dc=*/ 9, /* reset=*/ 8);

void setup(void)
{
  Serial.begin(9600);
  
  /* U8g2 Project: SSD1306 Test Board */
  //pinMode(10, OUTPUT);
  //pinMode(9, OUTPUT);
  //digitalWrite(10, 0);
  //digitalWrite(9, 0);			
  
  u8x8.begin();
  u8x8.setPowerSave(0);
  
  
}

void loop(void)
{
  if (Serial.available() > 0) {
  String data = Serial.readStringUntil('\n');
  Serial.print("Arduino got sent from Google Cloud: ");
  Serial.println(data);
  
  u8x8.setFont(u8x8_font_chroma48medium8_r);
  u8x8.drawString(0,1,"New Message:");
  u8x8.drawString(0,32, data.c_str());  
  delay(10000);
  }

  u8x8.fillDisplay();
 
}
