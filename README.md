# Phantom6G

Measurement and simulation system for Phantom6G project, to study the effects of 6G on human tissues.

# Electronics Project – Temperature Measurement in Phantom

The project is based on four main components:

1. **Temperature Sensors**  
   - Two-wire A733F thermistors (planned use of 12 sensors)  
   - Each sensor in a Wheatstone bridge configuration → precise resistance measurement  
   - Signal sampled by ESP32 microcontroller → calibration and conversion to °C  

2. **ESP32 Microcontroller**  
   - Receives signal from sensors  
   - Converts data and transmits it via USB to Raspberry Pi 5  

3. **Raspberry Pi 5**  
   - Acts as the application server and data storage  

4. **Web Application**  
   - Visualizes measurement results with graphs and simulation data  

---

### Technical Notes

- ESP32 has two ADC interfaces (ADC1 and ADC2) with 12-bit resolution (0–4095), which have limited stability and accuracy.  
- External ADC converters with 16–24 bit resolution are being considered.  
- Wi-Fi is not used because ADC2 is unavailable when Wi-Fi is active on ESP32.  
- Using 12 temperature sensors requires more ADC channels, justifying wired transmission and possible use of external ADCs.

# Projekt Elektroniki – Pomiar Temperatury w Fantomie

Projekt opiera się na czterech głównych komponentach:

1. **Czujniki temperatury**  
   - Dwuprzewodowe termistory A733F (planowane użycie 12 czujników)  
   - Każdy czujnik w układzie mostka Wheatstone’a → precyzyjny pomiar rezystancji  
   - Sygnał próbkowany przez mikrokontroler ESP32 → kalibracja i konwersja do °C  

2. **Mikrokontroler ESP32**  
   - Odbiera sygnał z czujników  
   - Konwertuje dane i przesyła je przewodowo (USB) do Raspberry Pi 5  

3. **Raspberry Pi 5**  
   - Pełni rolę serwera aplikacyjnego i magazynu danych  

4. **Aplikacja webowa**  
   - Wizualizacja wyników pomiarów w postaci wykresów i danych symulacyjnych  

---

### Uwagi techniczne

- ESP32 posiada dwa interfejsy ADC (ADC1 i ADC2) o rozdzielczości 12 bitów (0–4095), które mają ograniczoną stabilność i dokładność.  
- Rozważane jest zastosowanie zewnętrznych przetworników ADC 16–24 bitów.  
- Rezygnacja z Wi-Fi spowodowana jest tym, że podczas używania modułu Wi-Fi interfejs ADC2 jest niedostępny.  
- Przy 12 czujnikach konieczne jest użycie większej liczby kanałów ADC, co uzasadnia transmisję przewodową i zewnętrzny przetwornik.

---
