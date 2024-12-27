import os
import random
from generateKeyPair import generate_key_pair_from_password, write_keys_to_file, check_password, read_key

def create_user(name, password):
    #create directory for user in users folder
    os.mkdir(f"../users/{name}")
    #add data directory for user
    os.mkdir(f"../users/{name}/data")
    # get timestamp of folder creation
    timestamp = os.stat(f"../users/{name}").st_birthtime  
    # convert the timestamp to a string
    timestamp = str(timestamp)
   #generate a couple of keys for the user
    public, private = generate_key_pair_from_password(password, timestamp, 1024)
    #write the keys to a file
    write_keys_to_file("../users/", name, public, private)
    #store hashed password (for login)

def login_user(name, password):
    #Check if the name of the user exists
    if not os.path.exists(f"../users/{name}"):
        return False
    #get the timestamp of the user's folder
    timestamp = str(os.path.getctime(f"../users/{name}"))
    #check the password
    return check_password(name, password, timestamp)



if __name__ == "__main__":
    #test
    create_user("luna", "blabla13")
