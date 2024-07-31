#include <Arduino.h>
#include <FirebaseESP8266.h>
#include <ESP8266WiFi.h>
// Provide the token generation process info.
#include <addons/TokenHelper.h>

// Provide the RTDB payload printing info and other helper functions.
#include <addons/RTDBHelper.h>

#define WIFI_SSID "wifi의 ssid" // 연결 가능한 wifi의 ssid
#define WIFI_PASSWORD "wifi 비밀번호" // wifi 비밀번호
#define API_KEY "API_key"
#define USER_EMAIL "email"
#define USER_PASSWORD "pw"
#define DATABASE_URL "https://hatics-fa503-default-rtdb.firebaseio.com/" //<databaseName>.firebaseio.com or <databaseName>.<region>.firebasedatabase.app
#define DATABASE_SECRET "DATABASE_SECRET"

FirebaseData firebaseData;
FirebaseAuth auth;
FirebaseConfig firebaseConfig;

void setup() {
  Serial.begin(115200);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.println();
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
  }
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());
  Serial.println();

  // Firebase 설정
  Serial.println("Setting up Firebase...");
  firebaseConfig.database_url = DATABASE_URL; // URL 설정 
  firebaseConfig.api_key = API_KEY; // API 키 설정
  Firebase.reconnectNetwork(true);
  
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;
  firebaseData.setBSSLBufferSize(1024, 1024);
  firebaseData.setResponseSize(1024);
  firebaseConfig.token_status_callback = tokenStatusCallback; // see addons/TokenHelper.h

  Firebase.begin(&firebaseConfig, &auth); // Firebase 시작
  Firebase.setInt(firebaseData, "position", 0);
  pinMode(4, OUTPUT); //D2 연결 -위
  pinMode(5, OUTPUT); //D1 연결 -아래 
  pinMode(12, OUTPUT);//D6 연결 -왼
  pinMode(14, OUTPUT);//D5 연결 -오
}

void loop() {
  if (Firebase.getString(firebaseData, "position")) {
    String value = firebaseData.stringData();
    Serial.println(value);

    if (value == "1") { // 위
      analogWrite(4, 255);
      analogWrite(5, 0);
      analogWrite(12, 0);
      analogWrite(14, 0);
      Serial.println("위 모터 도는 중");
  	  delay(1000);
    } else if (value == "2") { // 아래 
      analogWrite(4, 0);
      analogWrite(5, 100);
      analogWrite(12, 0);
      analogWrite(14, 0);
      Serial.println("아래 모터 도는 중");
  	  delay(1000);
    } else if (value == "3") { // 왼쪽 
      analogWrite(4, 0);
      analogWrite(5, 0);
      analogWrite(12, 150);
      analogWrite(14, 0);
      Serial.println("왼쪽 모터 도는 중");
  	  delay(1000);
    } else if (value == "4") { // 오른쪽 
      analogWrite(4, 0);
      analogWrite(5, 0);
      analogWrite(12, 0);
      analogWrite(14, 200);
      Serial.println("오른쪽 모터 도는 중");
  	  delay(1000);
    } else if (value == "5") { // 전체 -원하는 위치 동작 
      analogWrite(4, 100);
      analogWrite(5, 100);
      analogWrite(12, 100);
      analogWrite(14, 100);
      Serial.println("전체 모터 도는 중");
  	  delay(2000);
    } else if (value == "6") { // 전체 - 카메라에 안 뜸 
      analogWrite(4, 100);
      analogWrite(5, 100);
      analogWrite(12, 100);
      analogWrite(14, 100);
      Serial.println("전체 모터 도는 중");
      delay(1000);
    }else if (value == "0"){
      analogWrite(4, 0);
      analogWrite(5, 0);
      analogWrite(12, 0);
      analogWrite(14, 0);
  }
  } else {
      analogWrite(4, 0);
      analogWrite(5, 0);
      analogWrite(12, 0);
      analogWrite(14, 0);
  }
}
