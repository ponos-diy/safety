import os

os.makedirs("output", exist_ok=True)

with open("output/safety.html", "w") as f:
    f.write("<html><body><h1>hello world</h1></body></html>")
