import sys
import requests

SERVER = "localhost:2334"

if __name__ == "__main__":
    if len(sys.argv) == 2:
        # get
        print(requests.get(
            f"http://{SERVER}/config/get/{sys.argv[1]}").content.decode())
    if len(sys.argv) == 3:
        # set
        print(requests.get(
            f"http://{SERVER}/config/set/{sys.argv[1]}/{sys.argv[2]}").content.decode())
