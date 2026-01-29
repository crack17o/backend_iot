# Code Arduino – ESP32-CAM RHYX M21-45 (complet à uploader)

Un seul sketch à copier dans l’IDE Arduino et à téléverser sur la carte **ESP32-CAM avec module RHYX M21-45** (capteur GC2145, 2MP, 1600×1200).  
Le brochage utilisé est celui de la carte type **AI-Thinker ESP32-CAM** (même PCB / même connecteur caméra).  
À configurer en haut du fichier : `WIFI_SSID`, `WIFI_PASSWORD`, `SERVER_HOST`, `API_KEY` (= `ESP32_API_KEY` côté Django).  
Dans l’IDE : **Outil → Carte → AI Thinker ESP32-CAM**.

---

## Code complet

```cpp
/*
 * ESP32-CAM RHYX M21-45 (module GC2145) – Envoi photo vers serveur parking
 * Brochage = AI-Thinker ESP32-CAM. Code complet à uploader sur la carte.
 */

#include "Arduino.h"
#include "WiFi.h"
#include "WiFiClient.h"
#include "esp_camera.h"
#include "soc/soc.h"

// ============== CONFIGURATION ==============
const char* WIFI_SSID     = "VOTRE_WIFI_SSID";
const char* WIFI_PASSWORD = "VOTRE_MOT_DE_PASSE_WIFI";
const char* SERVER_HOST   = "192.168.1.100";   // IP du PC où tourne Django
const uint16_t SERVER_PORT = 8000;
const char* API_KEY       = "CHANGE_ME_ESP32_KEY";  // Même valeur que dans parking_monitor/utils/constants.py (ESP32_API_KEY)
const unsigned long INTERVAL_MS = 15000;             // Envoi toutes les 15 secondes
// ==========================================

// Pins = AI-Thinker ESP32-CAM (compatible RHYX M21-45 / GC2145 sur même PCB)
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y2_GPIO_NUM        5
#define Y3_GPIO_NUM       18
#define Y4_GPIO_NUM       19
#define Y5_GPIO_NUM       21
#define Y6_GPIO_NUM       36
#define Y7_GPIO_NUM       39
#define Y8_GPIO_NUM       34
#define Y9_GPIO_NUM       35
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

void setup() {
  Serial.begin(115200);
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi OK");
  Serial.println(WiFi.localIP());

  camera_config_t config = {};
  config.ledc_channel    = LEDC_CHANNEL_0;
  config.ledc_timer      = LEDC_TIMER_0;
  config.pin_d0          = Y2_GPIO_NUM;
  config.pin_d1          = Y3_GPIO_NUM;
  config.pin_d2          = Y4_GPIO_NUM;
  config.pin_d3          = Y5_GPIO_NUM;
  config.pin_d4          = Y6_GPIO_NUM;
  config.pin_d5          = Y7_GPIO_NUM;
  config.pin_d6          = Y8_GPIO_NUM;
  config.pin_d7          = Y9_GPIO_NUM;
  config.pin_xclk        = XCLK_GPIO_NUM;
  config.pin_pclk        = PCLK_GPIO_NUM;
  config.pin_vsync      = VSYNC_GPIO_NUM;
  config.pin_href       = HREF_GPIO_NUM;
  config.pin_sscb_sda   = SIOD_GPIO_NUM;
  config.pin_sscb_scl   = SIOC_GPIO_NUM;
  config.pin_pwdn       = PWDN_GPIO_NUM;
  config.pin_reset      = RESET_GPIO_NUM;
  config.xclk_freq_hz   = 20000000;
  config.pixel_format   = PIXFORMAT_JPEG;
  config.frame_size     = FRAMESIZE_VGA;   // 640x480
  config.jpeg_quality  = 12;
  config.fb_count      = 1;
  config.grab_mode     = CAMERA_GRAB_WHEN_EMPTY;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Erreur caméra");
    return;
  }
  Serial.println("Caméra OK");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
    delay(2000);
    return;
  }

  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb || fb->len == 0) {
    if (fb) esp_camera_fb_return(fb);
    Serial.println("Capture échouée");
    delay(1000);
    return;
  }

  Serial.printf("Image %u octets\n", (unsigned)fb->len);

  WiFiClient client;
  if (!client.connect(SERVER_HOST, SERVER_PORT, 10000)) {
    Serial.println("Connexion serveur échouée");
    esp_camera_fb_return(fb);
    delay(5000);
    return;
  }

  const char* boundary = "----ESP32CAM----";
  String part1 = "POST /api/upload-image/ HTTP/1.1\r\n"
                 "Host: " + String(SERVER_HOST) + "\r\n"
                 "X-API-Key: " + String(API_KEY) + "\r\n"
                 "Content-Type: multipart/form-data; boundary=" + String(boundary) + "\r\n";
  String part2 = "\r\n--" + String(boundary) + "\r\n"
                 "Content-Disposition: form-data; name=\"image\"; filename=\"photo.jpg\"\r\n"
                 "Content-Type: image/jpeg\r\n\r\n";
  String part3 = "\r\n--" + String(boundary) + "--\r\n";

  size_t contentLen = part2.length() + fb->len + part3.length();
  part1 += "Content-Length: " + String(contentLen) + "\r\n\r\n";

  client.print(part1);
  client.print(part2);
  client.write(fb->buf, fb->len);
  client.print(part3);

  unsigned long t = millis();
  while (client.connected() && (millis() - t < 5000)) {
    if (client.available()) {
      String line = client.readStringUntil('\n');
      if (line.startsWith("HTTP/1.1")) {
        int code = line.substring(9, 12).toInt();
        Serial.printf("Réponse: %d\n", code);
        break;
      }
    }
    delay(10);
  }
  client.stop();
  esp_camera_fb_return(fb);

  delay(INTERVAL_MS);
}
```

---

Lancer Django avec : `python manage.py runserver 0.0.0.0:8000` pour accepter les requêtes du réseau local.

**RHYX M21-45 (GC2145)** : le module utilise le capteur GC2145 (2MP). La bibliothèque `esp32-camera` le gère avec le même brochage que l’AI-Thinker ; le JPEG est utilisé pour limiter le volume transféré. Si la carte ne démarre pas ou que la caméra échoue, vérifier dans l’IDE que la carte choisie est bien **AI Thinker ESP32-CAM** et que la version du noyau ESP32 est récente (support GC2145).
