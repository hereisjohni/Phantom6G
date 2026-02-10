from RsSmw import *
from time import sleep


class Generator_Virtual():
    def __init__(self, resource_name: str, id_query: bool = True, reset: bool = False, options: str = None, direct_session: object = None):
        print("Connected to VIRTUAL Signal Generator")
        return

    def com_check(self):
        print("Hello, I'm a VIRTUAL Signal Generator")
        return
    
    def meas_prep(self, mode, amplitude : int, freq : int):
        print(f"Updated Virt Gen Setup:{mode}, {amplitude}")
        return
    
    def set_output(self, set: bool):
        if(set):
            print("Started tansmition")
        else:
            print("Stoped Transmision")



class Generator(RsSmw):

    def __init__(self, ip_addres="192.168.8.30", port = 5025, connection_type = "SOCKET", phy_device = True):
        RsSmw.assert_minimum_version('5.0.44')
        self.resource = f'TCPIP::{ip_addres}::{port}::{connection_type}'  # Resource string for the device
        if phy_device:
            try:
                RsSmw.__init__(self, self.resource, True, True, "SelectVisa='socket'")
                self.com_check()
            except TimeoutError or ConnectionAbortedError:
                print("[TIMEOUT ERROR] Check is  computer and generator is connected to the same local network. Then try again.")
                exit()
        else:
            RsSmw.__init__(self, self.resource, True, True, "Simulate=True, DriverSetup=No, SelectVisa='socket'")
            self.com_check()      


    def com_check(self):
        self.visa_timeout = 500000  
        self.opc_timeout = 3000 
        self.utilities.instrument_status_checking = True
        self.repcap_hwInstance_set(repcap.HwInstance.InstA)


    def meas_prep(self, mode, amplitude : float, freq : float):
        self.source.frequency.set_mode(mode)
        self.source.power.level.immediate.set_amplitude(amplitude)
        self.source.frequency.fixed.set_value(freq)
        print(f'Channel 1 PEP level: {self.source.power.get_pep()} dBm')
        response = self.utilities.query_str('*IDN?')
        print(f'Direct SCPI response on *IDN?: {response}')

    def start_stop_generator(self, set: bool):
        self.output.state.set_value(set)
        msg = "Stardet transmision" if set  else "Stoped Transmision"
        print(msg) # Tylko do testów, w finalnej wersji usunąć bo spowalnia niepotrzebnie




if __name__ == "__main__":
    '''Example use'''
    Gen = Generator(ip_addres='192.168.1.20') # Utworzenie połączenia z generatorem za pomocą TCP/IP
    Gen.com_check() # Weryfikacja połączenia oraz ustawienie timeout dla virtualnej karty VISA i oczekiwania na odpowedź
    Gen.meas_prep(mode='CW', amplitude=10, freq=6.5E9) # Ustawienie parametrów na których ma pracować generator
    Gen.start_stop_generator(True) # Włączenie nadawania przez generator (domyślnie nie będzie nadawał a przynajmniej nie powinien)
    sleep(5) # generator nadaje przez 5 sekund
    Gen.start_stop_generator(False) # Wyłącze nadawania przez generator, Pamiętać o tym przy kończeniu pomiarów

