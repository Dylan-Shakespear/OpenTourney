# OpenTourney
Open Tourney is an in-development web-based tournament manager built with Python (Django)

#Setting up your local environment
Create a .env file in the projects root directory. Open the file and add the following line:
`SECRET_KEY=mysecretkey`
Replace `mysecretkey` with a secure and unique string of your choosing. You can use a tool like Django Secret Key 
Generator to generate a random secret key.

Save and close the .env file.

If you do not do this, the project will still run, just with a filler (not secure) secret key.
