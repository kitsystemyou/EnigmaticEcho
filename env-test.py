import os

print("start")
word = os.getenv("SCRIPT_WORD")
if word == "silver":
    print("env is silver🥈!!!!")
elif word == "gold":
    print("env is goldk🥇")
print("end")