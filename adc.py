import time
import sqlite3
import board
import digitalio
import re
import math

from datetime import datetime
from cedargrove_nau7802 import NAU7802

# ====== KONFIGURACJA EKSPERYMENTU ======
DB_NAME = 'projekt_phantom_6g.db'
CZĘSTOTLIWOŚĆ = 3.5      # GHz
MOC = 10.0               # dBm
NUMER_SONDY = 1

NUMER_SERYJNY = "CSP-211030257"

# ====== PARAMETRY FIZYCZNE ======
R_NOMINALNE = 11000.0    # Ohm
V_EX = 3.3               # V (Napięcie zasilania mostka)
G_WZMACNIACZ = 128     # Gain ustawiony w NAU7802 (standardowo 128)

# ====== KONFIGURACJA SPRZĘTOWA RPI ======
# Pin DRDY podłączony do GPIO 17
drdy = digitalio.DigitalInOut(board.D17)
drdy.direction = digitalio.Direction.INPUT

# Magistrala I2C
i2c = board.I2C()
nau7802 = NAU7802(i2c, address=0x2A, active_channels=1)

# ====== BAZA DANYCH ======
def inicjalizuj_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pomiary_phantom (
            timestamp TEXT NOT NULL,
            sonda INTEGER NOT NULL,
            volt REAL NOT NULL,
            freq REAL NOT NULL,
            moc REAL NOT NULL,
            temperature REAL NOT NULL
        )
    """)
    conn.commit()
    return conn

# ====== OBLICZENIA ======
def raw_to_mv(raw_value):
    """Konwertuje surową wartość 24-bitową na miliwolty.
    NAU7802 przy Gain 128 i Vref 3.3V ma zakres ok. +/- 25.78 mV full scale."""
    mv = (raw_value / 8388608.0) * (V_EX / G_WZMACNIACZ) * 1000.0
    return mv

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

# ====== ZAPIS DO DB ======
def zaloguj_dane(conn, sonda_nr, raw_val, freq, moc):
    mv = raw_to_mv(raw_val)
    volt_value = mv / 1000.0
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    impedancja_test = mv_na_R_Temp(mv, R_NOMINALNE, V_EX)
    temperature = R_Temp_na_TempC(impedancja_test)
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pomiary_phantom (timestamp, sonda, volt, freq, moc, temperature)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, sonda_nr, volt_value, freq, moc, temperature))

    conn.commit()

    print(f"{timestamp} | Nr_sondy: {NUMER_SERYJNY} | Raw: {raw_val:8f} | {volt_value:.6f} V | ΔR={impedancja_test:.4f} Ω | T={temperature:.2f}")

# ====== KONFIGURACJA ADC ======
def setup_adc():
    print("⚙️ Inicjalizacja NAU7802...")
    if not nau7802.enable(True):
        print("❌ BŁĄD: ADC nie odpowiada!")
        return False
    
    nau7802.gain = str(int(G_WZMACNIACZ))
    print(f"✅ Gain ustawiony na: {G_WZMACNIACZ}")
    
    print("⚖️ KALIBRACJA: Zdejmij obciążenie (3s)...")
    time.sleep(3)
    nau7802.calibrate("INTERNAL")
    nau7802.calibrate("OFFSET")
    print("🚀 System gotowy do pracy!")
    return True

# ====== MAIN ======
if __name__ == "__main__":
    conn = inicjalizuj_db(DB_NAME)
    
    if setup_adc():
        print("\n--- START LOGOWANIA DANYCH Z NAU7802 ---\n")
        try:
            while True:
                if drdy.value:
                    raw_value = nau7802.read()
                    zaloguj_dane(conn, NUMER_SONDY, raw_value, CZĘSTOTLIWOŚĆ, MOC)
                    time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n🛑 Zatrzymano przez użytkownika")
        finally:
            conn.close()
            print("✅ Baza danych zamknięta")
