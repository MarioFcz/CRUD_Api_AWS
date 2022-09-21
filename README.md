# Prueba Técnica PersonalSoft - Bancolombia #


Documentación a detalle del código, se presentarán pruebas de desarrollo, pruebas unitarias y muestras de resultados.

Código:

```Python
##################################################
########### IMPORTE DE LIBRERIAS #################
##################################################

import boto3
import json
import logging
from custom_encoder import CustomEncoder # Codificador requerido para realizar algunos tratamientos en JSON (custom_encoder.py)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

```
En este apartado tenemos todo lo referente a la importación de las librerías necesarias para que el procesamiento, conexión, codificación y registro de posibles errores.
```Python
import boto3
```
Nos permite realizar las conexiones desde Lambda hacia DynamoDB.

```Python
import json
```
Librería para lograr la manipulacion de los objetos en formato JSON.
```Python
import logging
```
Nos Permite obtener un registro de los posibles errores generados
```Python
from custom_encoder import CustomEncoder.
```
En este bloque se realiza la conexión hacia la base de datos DynamoDb y debemos especificar el nombre que hemos creado en la instancia.
```Python
##################################################
####### CONEXIÓN A BASE DE DATOS DYNAMO ##########
##################################################

dynamodbTableName = 'libreria'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)
```
En el caso de esta prueba el nombre de la base de datos corresponde a "libreria", por ende lo definimos de la siguiente manera:
```Python
dynamodbTableName = 'libreria'
```
Realizamos la conexión entre Lambda y DynamoDB con la siguiente linea de código
```Python
dynamodb = boto3.resource('dynamodb')
```
y por último por cuestiones de facilidad en el proceso de escritura definiremos la conexión a esta base de datos como "Table":
```Python
table = dynamodb.Table(dynamodbTableName)
```
Ahora es necesario realizar y definir los métodos que vamos a utilizar para realizar el CRUD de esta API y son los siguientes:
```Python
########################################################################################
####### Definición de métodos REST para realizar las peticiones a nuestra API ##########
########################################################################################

getMethod    = 'GET'
postMethod   = 'POST'
patchMethod  = 'PATCH'
deleteMethod = 'DELETE'
```
Metodo GET:
 (obtener datos)
```Python
getMethod    = 'GET'
```
Metodo POST:
(Enviar Datos)
```Python
postMethod   = 'POST'
```
Metodo PATCH:
(Actualizar Datos)
```Python
patchMethod   = 'PATCH'
```
Metodo DELETE:
(Eliminar Datos)
```Python
deleteMethod   = 'DELETE'
```
Definición de rutas:
```Python
########################################################################################
####### Definición de path's para realizar las peticiones requeridas ###################
########################################################################################

healthPath   =  '/health'
libroPath    = '/libro'
librosPath   = '/libros'
```
Ruta ```/health ``` nos permitirá obtener una respuesta del servidor y lograr conocer su estado.  
Ruta ```/libro ``` Es la ruta que vamos a emplear usualmente para realizar los procesos de: actualización, eliminación, consulta e insertar datos. (a detalle más adelante).  
Ruta ```/libros``` En esta ruta vamos a utilizar el metodo de obtener todos los datos de DynamoDB. 
  
   
Ahora vamos a definir las funciones y mostrar algunos resultados.  
Función Handler es la encargada de permanecer escuchando si llega un nuevo "evento" y reaccionar con la debida función.
```Python
####################################################
####### Definición de funciones  ###################
####################################################

def lambda_handler(event, context): 
    logger.info(event)
    httpMethod = event['httpMethod'] # Escuchamos el método que requerimos
    path = event['path']             # Escuchamos el path que vamos a utilizar
``` 
Ruta, función y resultados de ``` health ```:  
```Python
    # CONDICIONAL
    # Escuchamos el método GET y la ruta HEALTH
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
 ```  
 Ruta, función y resultados para la función de consulta de libro mediante su ID
 ```Python
    # CONDICIONAL
    # Escuchamos el método GET y la ruta LIBRO, obtenemos como párametro el ID del libro
    elif httpMethod == getMethod and path == libroPath:
        response = getLibro(event['queryStringParameters']['id'])
  ```  
  Función:
  ```Python
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
  ```  
  Pruebas:  
  Se utiliza como herramienta de ayuda el software 'POSTMAN' que nos sirve para verificar los resultados del servidor (TODOS LOS ARCHIVOS DE PRUEBAS SE ADJUNTAN EN LA CARPETA POSTMAN PARA UNA IMPORTACIÓN MÁS FÁCIL).  
  ## Importante!, la ruta para realizar las pruebas en AWS es la siguiente: 
  ```https://556l02jrr3.execute-api.us-east-1.amazonaws.com/Deploy/```  
  ### Para realizar la prueba de este endpoint se utiliza la ruta anterior seguido del path, quedando así:  
  ```https://556l02jrr3.execute-api.us-east-1.amazonaws.com/Deploy/libro``` 
  y utilizando el método GET, obteniendo algo similar a lo siguiente:  
  
  ![1](https://user-images.githubusercontent.com/43013600/191560022-67770cf8-845f-4393-9072-89c21269ad02.png)  
  
  Si envíamos la petición obtendremos la siguiente respuesta del servidor.  
  
  ![1 1](https://user-images.githubusercontent.com/43013600/191560240-44ad4c2f-5349-4787-b23a-5f6bf65ebfbc.png)

  ## Función para obtener todos los libros...
  
  ```Python
  # Condicional
  # Escuchamos el método GET y la ruta LIBROS.
    elif httpMethod == getMethod and path == librosPath:
        response = getLibros()
  ```  
  Función:  
  ```Python
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
  ```
  
  ## Pruebas
  
  ### Archivo de prueba con nombre ```Get_Libros```
  
  ![2](https://user-images.githubusercontent.com/43013600/191561918-431cd3a8-2fb6-4612-a668-8f1682dbf31f.png)  
  
  obtenemos como respuesta del servidor lo siguiente:
  
  ![2 1](https://user-images.githubusercontent.com/43013600/191562319-c57a42b8-5685-4fea-8161-aa66a7b23eb7.png)

## Condicional para insertar un nuevo libro...  
```Python
    # Condicional
    # Escuchamos el método POST y la ruta LIBRO.
    elif httpMethod == postMethod and path == libroPath:
        response = saveLibro(json.loads(event['body']))
```
## Función para insertar un nuevo libro...
  ```Python
  
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
        
  ```
  ## Pruebas:
  ### Archivo de prueba con nombre ```ADD_Libros```
  ![3](https://user-images.githubusercontent.com/43013600/191563731-5e168b56-1902-49ff-97ee-39da4e41ee81.png)
  
  ## Respuesta del servidor:  
  
![3 2](https://user-images.githubusercontent.com/43013600/191564451-eb448d45-3586-4bfa-89eb-66e2120dd9cb.png)  

## Condicional para actualizar un libro...
```Python
    # Escuchamos el método PATCH y la ruta LIBRO.
    elif httpMethod == patchMethod and path == libroPath:
        requestBody = json.loads(event['body'])
        response = modificarLibro(requestBody['id'], requestBody['CampoID'], requestBody['New_Valor'])
```
## Función para actualizar un libro...  
## Se inserta como párametros los datos ```ID``` para realizar la búsqueda del libro, ```CampoID```para insertar el campo que vamos a editar, ```New_Valor``` para asignar el nuevo valor de ese párametro.  
```Python
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
```  
## Pruebas...  
### Archivo de prueba con nombre ```Modify_Libros```

### Antes de mofidicar.

![4](https://user-images.githubusercontent.com/43013600/191565793-d4a01dea-6dbe-44b3-baf8-d2dd6b75d26a.png)

se realiza la petición de modificación, en este caso vamos a modificar "Antonia" por "Gabriela":  

![4 2](https://user-images.githubusercontent.com/43013600/191566050-5d29920c-d96e-40fa-9fb8-b39a21d6bf26.png)


y obtenemos como resultado lo siguiente...  

![4 3](https://user-images.githubusercontent.com/43013600/191566285-38564d3a-6fb9-409f-bf31-e92c3f656349.png)

dando como resultado exitoso, ahora vamos a comprobar utilizando un metodo anterior para ver si modifico la base de datos...

![4 4](https://user-images.githubusercontent.com/43013600/191566511-9dab24b2-9914-440f-af67-67a94a02ef34.png)  

## Por último vamos a comprobar la función para eliminar un libro. 

```Python
    ## Condicional
    # Escuchamos el método DELETE y la ruta LIBRO. 
    elif httpMethod == deleteMethod and path == libroPath:
        requestBody = json.loads(event['body'])
        response = deleteLibro(requestBody['id'])

    else:
        response = buildResponse(404,'Not Found')
    
    return response 
```  
## Función para eliminar un libro.  
```Python
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
        
```  

## Pruebas...  
### Archivo de prueba con nombre ```Delete_Libros```

 Vamos a eliminar el libro con nombre ```La Super Comedia```
 
 
![5](https://user-images.githubusercontent.com/43013600/191567104-e5d8f601-31c2-40e1-9e78-e1f6ad08cf8a.png)  

## Usamos la siguiente configuración en Postman


![5 1](https://user-images.githubusercontent.com/43013600/191567828-eac07113-58ed-4c93-9beb-b3e4c9555b49.png)

## Y como resultado obtenemos lo siguiente:  



![5 3](https://user-images.githubusercontent.com/43013600/191567955-83b1b770-225d-411f-93d6-c8ba50232549.png)  

## Función para retornar los respectivos Responses y el uso del Encoder en caso de que el cuerpo no sea Nulo.

```Python
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

```

