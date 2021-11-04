import boto3

s3 = boto3.resource('s3')
client = boto3.client('rekognition')
client.delete_collection(CollectionId='faces')
client.create_collection(CollectionId='faces')

def lista_imagens():
    imagens = []

    bucket = s3.Bucket('fa-imagens-reconhecimento')
    for imagem in bucket.objects.all():
        imagens.append(imagem.key)
    return imagens

def index_collection(imagens):
    for i in imagens:
        response=client.index_faces(
            CollectionId='faces',
            DetectionAttributes=[
            ],
            ExternalImageId=i[:-4],
            Image={
                'S3Object': {
                    'Bucket': 'fa-imagens-reconhecimento',
                    'Name': i,
                },
            },
        )

imagens = lista_imagens()
index_collection(imagens)


