from flask import Flask

#creating flask application
app=Flask(__name__)

@app.route('/')
def  index():
    return "This is index page"

if __name__=='__main__':
    app.run(host=localhost,port=8080,debug=True)
