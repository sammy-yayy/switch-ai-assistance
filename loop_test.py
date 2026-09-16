#For practicing and demo coding

def greet(name):
    print(f"Hello, {name} I am SWITCH")

while True:
    name = input("Enter your name(or type text): ")
    if name == "exit":
        break

    greet("Sam")

print("SWITCH is shutting down..")