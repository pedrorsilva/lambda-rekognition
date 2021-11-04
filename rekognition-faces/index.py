import boto3

from constants import COLLECTION_ID, IMAGE_BUCKET_NAME

s3 = boto3.resource('s3')
client = boto3.client('rekognition')

try:
  client.delete_collection(CollectionId=COLLECTION_ID)
except Exception:
  pass

try:
  client.create_collection(CollectionId=COLLECTION_ID)
except Exception:
  pass

def lista_imagens():
  imagens = []

  bucket = s3.Bucket(IMAGE_BUCKET_NAME)
  for imagem in bucket.objects.all():
      imagens.append(imagem.key)
  return imagens

def index_collection(imagens):
  for image in imagens:
    client.index_faces(
      CollectionId=COLLECTION_ID,
      DetectionAttributes=[
      ],
      ExternalImageId=image[:-4],
      Image={
        'S3Object': {
          'Bucket': IMAGE_BUCKET_NAME,
          'Name': image,
        },
      },
    )

imagens = lista_imagens()
index_collection(imagens)


