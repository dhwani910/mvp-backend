import bjoern
from app import app

host = '0.0.0.0'
port = 5000


print("Bjoern is running!")
bjoern.run(app,host,port)