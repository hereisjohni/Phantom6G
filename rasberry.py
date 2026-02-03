import sqlite3
import time
from datetime import datetime
import serial
import re
import math

SERIAL_PORT = '/dev/ttyUSB0' # TUTAJ DAJCIE '/dev/ttyUSB0'
BAUD_RATE = 115200
DB_NAME = 'projekt_phantom_6g.db'

CZĘSTOTLIWOŚĆ = 3.5  #GHz
MOC = 10.0
NUMER_SERYJNY = "CSP-211031316"

R_NOMINALNE = 11000.0 # 11 kOhm
V_EX = 3.3 #3.3V
G_WZMACNIACZ = 100.0

def inicjalizuj_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pomiary_phantom (
            timestamp DATETIME NOT NULL,
            sonda INTEGER NOT NULL,
            volt REAL NOT NULL, 
            freq REAL NOT NULL, 
            moc REAL NOT NULL,
            temperature REAL NOT NULL
        )
    """)
    conn.commit()
    return conn

def mv_na_R_Temp(mv_value, R_NOMINALNE, V_EX):
    V_wy = mv_value / 1000.0
    R = R_NOMINALNE * ((2 * V_EX) / (2 * V_wy + V_EX) - 1)
    return R


def R_Temp_na_TempC(R):
    if R <= 0:
        return float('nan')
        
    b0=0.000936245551
    b1=0.000251110924
    b2=-0.000000560727567
    b3=0.000000147898489
    
    logR = math.log(R)
    
    T = 1 / (b0 + b1 * logR + b2 * (logR**2) + b3 * (logR**3)) - 273.15
    return T

def zaloguj_dane(conn, sonda_nr, mv, freq, moc):
    volt_value = mv / 1000.0
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    cursor = conn.cursor()
    try:
        impedancja_test = mv_na_R_Temp(mv, R_NOMINALNE, V_EX)
        temperature = R_Temp_na_TempC(impedancja_test)

        cursor.execute("""
            INSERT INTO pomiary_phantom (timestamp, sonda, volt, freq, moc, temperature)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, sonda_nr, volt_value, freq, moc, temperature))

        conn.commit()
        
        print(
            f"💾 Zapisano: {timestamp} | {volt_value:.6f} V | Freq: {freq} GHz | Impedancja: {impedancja_test:.4f} Ohm | Temperatura: {temperature}")

    except Exception as e:
        print(f"❌ Błąd zapisu do bazy danych: {e}")

if __name__ == "__main__":
    
    conn = inicjalizuj_db(DB_NAME)

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) 
        time.sleep(2)
        ser.flushInput()
        print(f"✅ Połączono z portem: {SERIAL_PORT} (Prędkość: {BAUD_RATE})")
        print(f"Dane symulacyjne")
        print(f"Częstotliwość: {CZĘSTOTLIWOŚĆ} GHz")
        print(f"Moc: {MOC}")
        print(f"Numer seryjny czujnika Amphenol A733F-CSP60BT103M: {NUMER_SERYJNY}")
        
    except serial.SerialException as e:
        print(f"❌ Błąd: Nie można połączyć z portem {SERIAL_PORT}. Sprawdź kabel i port. Błąd: {e}")
        exit()

    print("\n--- Rozpoczynanie logowania danych z ESP32 ---")

    try:
        while True:
            
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()

                if line:
                    try:
                        if ',' not in line and re.match(r"^-?\d+(\.\d+)?$", line):
                            mv_value = float(line)
                        
                        elif ',' in line:
                            parts = line.split(',')
                            if len(parts) == 2 and parts[0].startswith('Sonda'):
                                mv_value = float(parts[1])
                            else:
                                print(f"⚠️ Nieznany format danych: {line}")
                                continue
                        else:
                            print(f"⚠️ Odrzucono nieznany format danych: {line}")
                            continue

                        zaloguj_dane(conn, NUMER_SERYJNY, mv_value, CZĘSTOTLIWOŚĆ, MOC)

                    except ValueError:
                        print(f"❌ Błąd konwersji liczby (sprawdź format danych z ESP32): {line}")
                    except Exception as e:
                        print(f"❌ Nieoczekiwany błąd przetwarzania: {e}")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n\n🛑 Przerwanie przez użytkownika. Zamykanie połączeń.")
    finally:
        ser.close()
        conn.close()
        print("✅ Połączenia zamknięte. Koniec programu.")
