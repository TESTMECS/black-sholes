from api.flask_app import application

if __name__ == "__main__":
    application.run(host="localhost", port=5000, debug=True)

