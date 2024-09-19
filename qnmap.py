#!/usr/bin/python3
# qnmap.py
# Description: Simple script to automate NMAP scanning
# Author: Attaxika
# Date: 4/8/2024

#Imports
import os
import sys
import ipaddress
import subprocess

#Auto-complete imports
try:
    try:
        if "posix" in os.name:
            import readline
        else:
            print("You are not on a unix operating system. Tab-completion for paths will not work")
    except ImportError:
        print("You do not have readline installed. Installing... (Ctrl+C to cancel this request)")
        try:
            os.system("pip install readline")
        except Exception as e:
            print("Failed to install readline. Tab-completion will not work")
            print(e)
except KeyboardInterrupt:
    print("Cancelled installation of packages. Tab-completion will not work")

#Variables
commandQueue = []
installedScripts = []

#Main
def main():
    print("QNMAP")
    #Load all scripts that are installed
    if "posix" in os.name:
        installedScripts.extend(os.system("ls /usr/share/nmap/scripts/"))
    else:
        installedScripts.extend(os.listdir("C:/Program Files (x86)/Nmap/scripts/"))

    finishedCheck = False
    finished = False
    try:
        while not finished:
            finishedCheck = False
            print("Build command %s" % (len(commandQueue) + 1))
            commandQueue.append(commandBuilder())
            while not finishedCheck:
                next = input("Add another command? (y/n) ").lower()
                if next == "y":
                    finishedCheck = True
                elif next == "n":
                    finishedCheck = True
                    finished = True
                else:
                    print("Invalid input.")
        print("Command creation complete. %s commands created." % len(commandQueue))
        print("Do these look okay? (y/n)")
        for count, command in enumerate(commandQueue):
            print("%s ) %s" % (count + 1, command))
        if "y" not in input().lower():
            print("Exiting...")
            sys.exit()
        #Check if directory exists
        if not os.path.exists("nmaplogs"):
            print("Creating nmaplogs directory...")
            try:
                os.system("mkdir nmaplogs")
            except Exception as e:
                print("[Likely a directory creation error] Error: %s" % e)
                print("Run in terminal instead? (y/n)")
                if "y" in input().lower():
                    for command in commandQueue:
                        os.system(command)
                else:
                    print("Exiting...")
                    sys.exit()
        for count, command in enumerate(commandQueue):
            os.chdir("nmaplogs")
            try:
                subprocess.Popen(command, stdout=open("nmap_{}".format(count + 1), "w"))
            except Exception as e:
                print("[Malformed nmap command/process error] Error: %s" % e)
                print("Skipping...")
                continue
            

    except KeyboardInterrupt:
        print("Exiting...")

#IP validate
def validate_ip(ip):
    try:
        ipaddress.ip_network(ip, strict=False)
        return True
    except ValueError:
        return False
    
#Command builder
def commandBuilder() :
    argList = ["-sU", "-sV", "-sS", "-sT", "-sA", "-sF", "-O", "-A", "-T", "-Pn","-sn","--script="]
    argChoice = []
    scriptList = []
    port_selection = "-p 0-1000"
    ports = False
    complete = False
    while not complete:
        nextCheck = False
        scriptCheck = False
        for count, item in enumerate(argList):
            print("%s ) %s" % (count + 1, item))
        print("Exclusive options will be removed once their exclusive counterpart is selected.")
        userInput = input("Select option: ")

        #Check for programmatically invalid choice:
        try:
            if int(userInput) > len(argList) or int(userInput) < 1:
                print("[1]Invalid choice.")
            else:
                #Check for invalid script choice
                if not "script" in argList[int(userInput)-1]:
                    argChoice.append(argList[int(userInput)-1])
                    userChoice = argList[int(userInput)-1]
                    #Check for exclusive options and then delete user choice & exclusive counterpart
                    if userChoice == "-sS":
                        argList.remove("-sS")
                        argList.remove("-sT")
                        argList.remove("-sn")
                    elif userChoice == "-sT":
                        argList.remove("-sS")
                        argList.remove("-sT")
                        argList.remove("-sn")
                    elif userChoice == "-sU":
                        argList.remove("-sU")
                        argList.remove("-sF")
                        argList.remove("-sn")
                    elif userChoice == "-sF":
                        argList.remove("-sU")
                        argList.remove("-sF")
                        argList.remove("-sA")
                        argList.remove("-sn")
                    elif userChoice == "-sA":
                        argList.remove("-sA")
                        argList.remove("-sF")
                        argList.remove("-sU")
                        argList.remove("-sn")
                    elif userChoice == "-sn":
                        argList.remove("-sn")
                        argList.remove("-sU")
                        argList.remove("-sF")
                        argList.remove("-sA")
                    else:
                        argList.remove(userChoice)
                else:
                    scriptLoop = True
                    while scriptLoop:
                        scriptCheck = False
                        print("Enter a script name. You may use a built-in script or a custom script.")
                        print("For built in scripts, you may type 'show' to see a list.")
                        print("For custom scripts, you will have to use a path to the script.")
                        #Check if readline was imported
                        if "readline" in sys.modules:
                            script = readline.parse_and_bind("tab: complete").input("Script: ").lower()
                        else:
                            script = input("Script: ").lower()
                        if os.path.exists(script):
                            scriptList.append(script)
                        elif script in installedScripts:
                            scriptList.append(script)
                        elif script == "show":
                            for i in installedScripts:
                                print(i)
                            scriptCheck = True
                        else:
                            print("Invalid script.")
                            scriptCheck = True
                        while not scriptCheck:
                            next = input("Add another script? (y/n) ").lower()
                            if next == "y":
                                scriptCheck = True
                            elif next == "n":
                                scriptCheck = True
                                scriptLoop = False
                            else:
                                print("[2]Invalid choice.")
                #Prompt for another argument
                while not nextCheck:
                    next = input("Add another argument? (y/n) ").lower()
                    if next == "y":
                        nextCheck = True
                    elif next == "n":
                        nextCheck = True
                        complete = True
                    else:
                        print("[3]Invalid choice.")
        except ValueError as e:
            print(e)
            print("[4]Invalid choice.")
    invalidIP = True
    while invalidIP:
        ip = input("Enter IP: ")
        if validate_ip(ip):
            invalidIP = False
    if input("Select ports? If 'n', will use default range (y/n) ").lower() == "y":
        ports = True
    else:
        ports = False
    if ports:
        print("Separate ports with commas, or type ONE range of ports.")
        ports = input("Enter ports: ").split(",")
        if "-" in ports[0]:
            ports = ports
        else:
            ports = list(map(int, ports))
        ports_str = ",".join(map(str, ports))
        port_selection = "-p {}".format(ports_str)

    if scriptList:
        builtCommand = "nmap %s %s --script %s %s" % (" ".join(argChoice), port_selection, ",".join(scriptList), ip)
    else:
        builtCommand = "nmap %s %s %s" % (" ".join(argChoice), port_selection, ip)
    return builtCommand

#Main call
if __name__ == "__main__":
    main()
