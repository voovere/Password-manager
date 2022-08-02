import os
from pymongo import MongoClient
import pymongo
import bcrypt
from cryptography.fernet import Fernet

#konsoles valymas
clear = lambda: os.system("cls")

#pagrindinio meniu pasirinkimai
main_menu_options = {
    1: "Registruotis",
    2: "Prisijungti",
    3: "Uzdaryti",
}

#prisijungimo meniu pasirinkimai
login_menu_options = {
    1: "Iterpti nauja slaptazodi",
    2: "Pateikti issaugotus slaptazodzius",
    3: "Istrinti norima slaptazodi",
    4: "Atsijungti",
}

#prisijungimas prie db
def get_database():
    CONNECTION_STRING = "mongodb+srv://admin:aJRNpWg5fdkiiPs0@nordpass.7oiqs.mongodb.net/NordPass?retryWrites=true&w=majority"
    client = MongoClient(CONNECTION_STRING)
    return client["NordPass"]

#pagrindinio meniu spausdinimas
def print_main_menu():
    print("NordPass but its console")
    print("------------------------")
    for key in main_menu_options.keys():
        print ("[", key, "] ", main_menu_options[key] )

#prisijungimo meniu spausdinimas
def print_login_menu(user):
    print("Sveiki,", user["username"])
    print("------------------------")
    for key in login_menu_options.keys():
        print ("[", key, "] ", login_menu_options[key] )

#rakto generavimas
def generate_key():
    key = Fernet.generate_key()
    return key

#registravimo funkcija
def register(userCollection):
    clear()
    print("Registracija")
    print("------------------------")

    print("Iveskite vartotojo varda:")
    name = input()

    print("Iveskite slaptazodi:")
    password = input()

    print("Pakartokite slaptazodi:")
    confirmPassword = input()

    userDetails = userCollection.find({})
    found = False

    for usr in userDetails:
        if name == usr["username"]:
            found = True
            break


    if found == False:
        if password == confirmPassword:
            key = generate_key()
            password = password.encode("utf-8")
            user = {
                "username": name,
                "password": bcrypt.hashpw(password, bcrypt.gensalt()),
                "key": key
            }
            userCollection.insert_one(user)
            print("Sekmingai prisiregistravote")
        else:
            print("Slaptazodziai nesutampa")
    else:
        print("Toks vartotojas jau egzistuoja")

    print("Spauskite bet kuri klavisa, kad griztumet i meniu")
    input()
    clear()

#prisijungimo funkcija
def login(userCollection, passwordCollection):
    clear()
    print("Prisijungimas")
    print("------------------------")

    print("Iveskite vartotojo varda:")
    name = input()

    print("Iveskite slaptazodi:")
    password = input()
    password = password.encode("utf-8")

    userDetails = userCollection.find({})
    found = False

    for usr in userDetails:
        if name == usr["username"]:
            found = True
            if bcrypt.checkpw(password, usr["password"]):
                clear()
                while(True):
                    print_login_menu(usr)
                    option = ""
                    try:
                        option = int(input("Iveskite pasirinkima: "))
                    except:
                        print("Blogas pasirinkimas...")
                        print("Spauskite bet kuri klavisa, kad griztumet i meniu")
                        input()
                        clear()
                    if option == 1:
                        insert_site(usr, passwordCollection)
                    elif option == 2:
                        show_all_sites(usr, passwordCollection)
                    elif option == 3:
                        del_sites(usr, passwordCollection)
                    elif option == 4:
                        clear()
                        break
                    else:
                        print("Blogas pasirinkimas")
                        print("Spauskite bet kuri klavisa, kad griztumet i meniu")
                        input()
                        clear()
            else:
                print("Blogas slaptazodis")
    if found == False:
        print("Vartotojas nerastas")
    else:
        print("Viso gero ;)")

    print("Spauskite bet kuri klavisa, kad griztumet i meniu")
    input()
    clear()

#pridedamas slaptazodis i db
def insert_site(usr, passwordCollection):
    clear()
    print("Prideti nauja slaptazodi")
    print("------------------------")
    print("Iveskite svetaines pavadinima:")
    site = input()

    print("Iveskite slaptazodi:")
    password = input()

    all_pass = passwordCollection.find({"user": usr["_id"]})
    found = False

    for p in all_pass:
        if p["site"] == site:
            found = True

    if found == False:
        password = password.encode()
        f = Fernet(usr["key"])
        encoded = f.encrypt(password)

        site = {
            "user": usr["_id"],
            "site": site,
            "password": encoded
        }

        passwordCollection.insert_one(site)
        print("Slaptazodis irasytas")
    else:
        print("Tokia svetaine jau irasyta")
    
    print("Spauskite bet kuri klavisa, kad griztumet i meniu")
    input()
    clear()

#spausdinami visi slaptazodziai susije su prisijungusiu useriu
def show_all_sites(usr, passwordCollection):
    clear()
    print("Visi slaptazodziai")
    print("------------------------")

    user_data = passwordCollection.find({"user": usr["_id"]})
    f = Fernet(usr["key"])
   
    for user in user_data:
        decoded = f.decrypt(user["password"])
        print("Svetaine:", user["site"], "Slaptazodis:", decoded.decode())

    print("Spauskite bet kuri klavisa, kad griztumet i meniu")
    input()
    clear()

#panaikinamas pasirinktas slaptazodis
def del_sites(usr, passwordCollection):
    clear()
    print("Istrinti slaptazodzius")
    print("------------------------")
    print("Iveskite svetaines pavadinima:")
    site = input()

    passwordCollection.delete_one({"user": usr["_id"], "site": site})

    print("Slaptazodis sekmingai istrintas")
    print("Spauskite bet kuri klavisa, kad griztumet i meniu")
    input()
    clear()

#main funkcija
if __name__=="__main__":
    #prisijungimas prie db
    db = get_database()
    userCollection = db["user"]
    passwordCollection = db["password"] 

    while(True):
        print_main_menu()
        option = ""
        try:
            option = int(input("Iveskite pasirinkima: "))
        except:
            print("Blogas pasirinkimas...")
            print("Spauskite bet kuri klavisa, kad griztumet i meniu")
            input()
            clear()
        #registracijos funkcija
        if option == 1:
           register(userCollection)
        #prisijungimo funkcija
        elif option == 2:
            login(userCollection, passwordCollection)
        #programos uzdarymas
        elif option == 3:
            print("Viso gero ;)")
            exit()
        else:
            print("Blogas pasirinkimas")
            print("Spauskite bet kuri klavisa, kad griztumet i meniu")
            input()
            clear()