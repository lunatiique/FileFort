import os
from generate_key_pair import generate_key_pair_from_password, write_keys_to_file

def create_user(name, password):
    #create directory for user in usesrs folder
    os.mkdir(f"../users/{name}")
    #create a file for the user in the users folder
    with open(f"../users/{name}/password.txt", "w") as f:
        f.write(password)
   #generate a couple of keys for the user
    public, private = generate_key_pair_from_password(password, 1024)
    #write the keys to a file
    write_keys_to_file("../users/", name, public, private)

#if __name__ == "__main__":
    #create_user("alice", "ccleszouavessssssss")