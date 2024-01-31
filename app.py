from website import create_app
from flask import session

app = create_app()

if __name__ == 'main':
    app.run(debug=True)
    
