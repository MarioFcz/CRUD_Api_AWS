##################################################
########### IMPORTE DE LIBRERIAS #################
##################################################

'En este apartado se realiza la importación de todas las librerías necesarias para que la aplicación funcione sin problema en AWS Lambda'

import boto3
import json
import logging
from custom_encoder import CustomEncoder # Codificador requerido para realizar algunos tratamientos en JSON (custom_encoder.py)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

##################################################
####### CONEXIÓN A BASE DE DATOS DYNAMO ##########
##################################################

'Con los siguientes códigos podemos realizar la conexión a la base de datos DynamoDB'

dynamodbTableName = 'libreria'  # Aquí especificamos el nombre de nuestra base de datos previamente definida en AWS
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

########################################################################################
####### Definición de métodos REST para realizar las peticiones a nuestra API ##########
########################################################################################

getMethod    = 'GET'
postMethod   = 'POST'
patchMethod  = 'PATCH'
deleteMethod = 'DELETE'

########################################################################################
####### Definición de path's para realizar las peticiones requeridas ###################
########################################################################################

healthPath   =  '/health'
libroPath    = '/libro'
librosPath   = '/libros'


####################################################
####### Definición de funciones  ###################
####################################################

def lambda_handler(event, context):  # Función Handler es la encargada de permanecer escuchando si llega un nuevo "evento" y reaccionar con la debida función
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']

###############################################################################################
####### Condicionales que nos permiten actuar en cada uno de las peticiones ###################
###############################################################################################

   # Con esta ruta nos podemos asegurar si el servidor se encuentra operando correctamente
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
        
    # Con esta ruta podemos consultar un libro mediante su ID y con un método GET
    elif httpMethod == getMethod and path == libroPath:
        response = getLibro(event['queryStringParameters']['id'])
        
    # Con esta ruta podemos obtener todos los libros que se encuentran en nuestra base de datos
    elif httpMethod == getMethod and path == librosPath:
        response = getLibros()
        
    # Con esta ruta podemos insertar un nuevo libro a nuestra base de datos con método POST
    elif httpMethod == postMethod and path == libroPath:
        response = saveLibro(json.loads(event['body']))

    # Con esta ruta podemos realizar la actualización de un campo en cualquier libro que lo necesite    
    elif httpMethod == patchMethod and path == libroPath:
        requestBody = json.loads(event['body'])
        response = modificarLibro(requestBody['id'], requestBody['CampoID'], requestBody['New_Valor'])

    # Con esta ruta podemos eliminar un registro de la base de datos   
    elif httpMethod == deleteMethod and path == libroPath:
        requestBody = json.loads(event['body'])
        response = deleteLibro(requestBody['id'])

    else:
        response = buildResponse(404,'Not Found')
    
    return response 
    
###############################################################################################
####### Función para obtener un libro de nuestra base de datos mediante su ID #################
###############################################################################################

def getLibro(id):  # Recibimos como párametro el ID 
    try:
        # Búsqueda de registro mediante párametro
        response = table.get_item(
            Key ={
                'id':id
            }
        )
        # en caso de que exista dicho párametro lo mostramos y retornamos
        if 'Item' in response:
            return buildResponse(200, response['Item'])

        # Respondemos con un código 404 en caso de que no exista
        else:
            return buildResponse(404,{'Message':'Not Found'})

    # Añadimos un logger que nos permite tener un LOG en AWS CloudWatch
    except:
        logger.exception('Error!')


###############################################################################################
####### Función para obtener todos los libros de nuestra base de datos ########################
###############################################################################################

def getLibros():
    try:

        # Realizamos un escaneo a toda la base de datos y retornamos todos los valores encontrados 
        response = table.scan()
        result = response['Items'] # Almacenamiento de los resultados
        body = {
                'Libros': result
            }
        return buildResponse(200, body)

    # Añadimos un logger que nos permite tener un LOG en AWS CloudWatch      
    except:
        logger.exception('Error!')


#######################################################################################
####### Función para insertar un libro a nuestra base de datos ########################
#######################################################################################

def saveLibro(requestBody): # Ingresa como párametro el JSON donde se encuentra toda la información del libro, tal como, Author, Id, Nombre, Editorial
    try:
        table.put_item(Item=requestBody)
        body = {
            'Estado':'Guardado',
            'Item': requestBody
        }
        return buildResponse(200, body)
    
    # Añadimos un logger que nos permite tener un LOG en AWS CloudWatch   
    except:
        logger.exception('Error!')


#######################################################################################
####### Función para modificar un libro a nuestra base de datos #######################
#######################################################################################

def modificarLibro(id, CampoID, New_Valor): # Párametros necesarios para realizar el cambio o modificación de información
    try:
        response = table.update_item(
            Key={
                'id':id  # Seleccionamor como párametro de búsqueda el ID del libro
            },
            UpdateExpression='set %s =:value' % CampoID,  # con CampoID, definimos el campo que vamos a modficar
            ExpressionAttributeValues={
                ':value':New_Valor # Con New_Valor, definimos el nuevo valor para dicho campo
            },
            ReturnValues='UPDATED_NEW'
        )
        body = {
            'Estado':'Actualizado',
            'Actualizado': response  # Respondemos con la actualización realizada y el estado exitoso
        }
        return buildResponse(200, body)

    # Añadimos un logger que nos permite tener un LOG en AWS CloudWatch
    except:
        logger.exception('Error!')

#######################################################################################
####### Función para eliminar un libro de nuestra base de datos #######################
#######################################################################################      

def deleteLibro(id): # Párametro de entrada para realizar la búsqueda de nuestro libro 
    try:
        response = table.delete_item(  # Entrada de DynamoDb que realiza la eliminación del item con su respectivo ID
            Key={
                'id': id
            },
            ReturnValues = 'ALL_OLD'
        )
        body = {
            'Estado':'Eliminado',
            'Libro_eliminado':response  # Retornamos la respuesta del item eliminado y el estado
        }
        return buildResponse(200, body)

    # Añadimos un logger que nos permite tener un LOG en AWS CloudWatch  
    except:
        logger.exception('Error!')
        
#######################################################################################
####### Función para realizar los respectivos Responses, con su StatusCode ############
####################################################################################### 

def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response