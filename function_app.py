import azure.functions as func
import logging
import pyodbc
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="LearnFuncDeployment")
def LearnFuncDeployment(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name == "magic":

        #Getting secret frmo AKC
        try:
            logging.info('Attempting to get secret from key vault')
            key_vault_url = "https://learnazdeployment.vault.azure.net/"
            credential = DefaultAzureCredential()

            client = SecretClient(vault_url=key_vault_url,credential=credential)

            sql_user_name = client.get_secret("sqluser").value
            sql_password = client.get_secret("sqlpassword").value

            logging.info('Test')

            logging.info('Successfully retrieve the credentials')
        except:
            logging.info("Exception caught attempting to get secrets from AKV")
            return func.HttpResponse("Exception caught attempting to get secrets from AKV", status_code=500)

        #connecting to SQL
        server = 'azfuncdeployment.database.windows.net'
        database = 'AzFuncDeployment'
        driver = '{ODBC Driver 17 for SQL Server}'

        try:

            logging.info('Attempting to connect to SQL DB')

            connection_string = 'DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+sql_user_name+';PWD='+sql_password
            
            cnxn = pyodbc.connect(connection_string)
        
        except pyodbc.Error as ex:
            logging.info("Exception caught attempting to connect to SQL DB")
            logging.info(ex)
            return func.HttpResponse("Exception caught attempting to connect to SQL DB", status_code=500)

        # executing SQL query
        all_records_sqlry = 'select * from inventory'
        car_models = []

        try:
            with cnxn.cursor() as cursor:
                cursor.execute(all_records_sqlry)
                rows = cursor.fetchall()

                for row in rows:
                    logging.info(row)
                    car_models.append(row[2])
            return func.HttpResponse(f'{car_models}')
        except pyodbc.Error as ex:
            logging.info("Exception caught attempting execute SQL query")
            logging.info(ex)
            return func.HttpResponse("Exception caught attempting to execute SQL query", status_code=500)

    else:
        return func.HttpResponse("This HTTP triggered function executed successfully. You didn't pass the correct name though, try again", status_code=200)