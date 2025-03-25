from pymongo import MongoClient
from bson import ObjectId
# URL de conexión a MongoDB (ajusta según tu configuración)
mongo_url = "mongodb://localhost:27017/"

# Nombre de la base de datos
nombre_bd = "cancer"

try:
    # Crear un cliente de MongoDB
    cliente = MongoClient(mongo_url)

    # Acceder a la base de datos
    db = cliente[nombre_bd]

    # Listar las colecciones disponibles en la base de datos
    collection = db.list_collection_names()
    
    if __name__ == "__main__":
        print(f"Conexión exitosa a la base de datos: {nombre_bd}")
        print("Colecciones disponibles:")
        for collection in collection:
            print(f"- {collection}")


except Exception as e:
    print(f"Error al conectar con MongoDB: {e}")

def upload2DB(document, collection=db["cancerImages"]):
    """
    This function uploads a document to the MongoDB database
    :param document: the document to upload
    :return: the document id
    """
    try:
        # Insertar el documento en la colección
        resultado = collection.insert_one(document)
        return resultado.inserted_id
    except Exception as e:
        raise ValueError(f"Error al subir el documento a la base de datos: {str(e)}")
    
def getDocument(document_id=None, collection=db["cancerImages"]):
    """
    This function retrieves a document or all documents from the MongoDB database
    :param document_id: the document id (optional)
    :return: the document or all documents
    """
    try:
        if document_id:
            # Buscar el documento por su ID
            documento = collection.find_one({"_id": ObjectId(document_id)})
        else:
            # Obtener todos los documentos
            documento = list(collection.find())
        return documento
    except Exception as e:
        raise ValueError(f"Error al obtener el documento de la base de datos: {str(e)}")

def deleteDocument(document_id, collection=db["cancerImages"]):
    """
    This function deletes a document from the MongoDB database
    :param document_id: the document id
    :return: the result of the deletion
    """
    try:
        # Eliminar el documento por su ID
        resultado = collection.delete_one({"_id": document_id})
        return resultado
    except Exception as e:
        raise ValueError(f"Error al eliminar el documento de la base de datos: {str(e)}")
    
    
    
    
