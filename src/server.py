from flask import Flask
from flask_classful import FlaskView, route

app = Flask(__name__)

class MyServer(FlaskView):
  def __init__(self):
    pass

  @route('/getSomeData')
  def getSomeData():
    return random.choice(globalData) #select some random data to return


MyServer.register(app, base_route="/")


if __name__ == "__main__":
  app.run(host='0.0.0.0')
