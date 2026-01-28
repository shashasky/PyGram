import os
from dotenv import load_dotenv
load_dotenv()
from bootstrap.app import create_app
app = create_app()
app.run()