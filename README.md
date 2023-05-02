# Para Statistics

### Documentation
Requirements:
- Latest version of Python
- Locally hosted MongoDB on port 27017. (Docker recommended)
- Credentials from the Para backend. (https://paraio.com)
    - application access key
    - application secret
- MongoDB Database Tools (used for Mongomport) (https://www.mongodb.com/docs/database-tools/mongoimport/)

Steps to run it yourself:
1. Install packages `'matplotlib'`, `'pymongo'`, `'requests'` and `'requests_auth_aws_sigv4'` with Pip
1. Create a python file named `secret.py` in the root folder and add the Para access key and secret to this file as variables.
    - Example: `access_key='<VALUE>' secret='<VALUE>'`
1. Install MongoDB Database Tools, navigate to the folder you've installed it to. Copy the `mongoimport.exe` and paste it in to the root folder. (This is used to import the Para database locally)
1. Run the `main.py` Python file

What does it do?
1. Export the Para database using the given credentials
    - Para doesn't support directly communicating to the MongoDB so this is done via an export.
1. Import the exported data from Para to your local MongoDB instance
    - `mongoimport.exe` is used for this step
1. A MongoDB query is run on the local MongoDB to fetch the required data for the visualisation.

Info:
- All Para data is imported in this process so you are not limited to what the Python script presents.
- The steps `1` and `2` only need to run once, you can remove the locally created folder `'export/'` and remove the local MongoDB collection `'para'` to fetch the latest data again from Para.