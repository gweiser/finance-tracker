from website import create_app
from flask import session

app = create_app()

if __name__ == 'main':
    print("Hello, world!")
    app.run(debug=True)
    
