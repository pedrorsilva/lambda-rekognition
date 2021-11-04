from typing import Collection
import boto3
import json

client = boto3.client('rekognition')
s3 = boto3.resource('s3')

def detecta_faces():
    faces_detectadas=client.index_faces(
        CollectionId='faces',
        DetectionAttributes=['DEFAULT'],
        ExternalImageId='TEMPORARIA',
        Image={
            'S3Object': {
                'Bucket': 'fa-imagens-reconhecimento',
                'Name': '_analise.jpg',
            },
        },
    )

    return faces_detectadas

def cria_lista_faceid_detectadas(faces_detectadas):
    faceid_detectadas = []

    for index in range(len(faces_detectadas['FaceRecords'])):
        faceid_detectadas.append(faces_detectadas['FaceRecords'][index]['Face']['FaceId'])

    return faceid_detectadas
    
def compara_imagens(faceid_detectadas):
    resultado_comparacao = []
    for id in faceid_detectadas:
        resultado_comparacao.append(
            client.search_faces(
                CollectionId='faces',
                FaceId=id,
                FaceMatchThreshold=80,
                MaxFaces=10
            )
        )
    return resultado_comparacao

def gera_dados_json(resultado_comparacao):
    dados_json = []
    for face_match in resultado_comparacao:
        if len(face_match.get('FaceMatches')) >= 1:
            perfil = dict(nome=face_match['FaceMatches'][0]['Face']['ExternalImageId'], 
            faceMatch = round(face_match['FaceMatches'][0]['Similarity'], 2))

            dados_json.append(perfil)

    return dados_json

def publica_dados(dados_json):
    arquivo = s3.Object('fa-site-s3', 'dados.json')
    arquivo.put(Body=json.dumps(dados_json))

def exclui_imagem_colecao(faceid_detectadas):
    client.delete_faces(
        CollectionId='faces',
        FaceIds=faceid_detectadas
    )

def main(event, context):
    faces_detectadas = detecta_faces()
    faceid_detectadas = cria_lista_faceid_detectadas(faces_detectadas)
    resultado_comparacao = compara_imagens(faceid_detectadas)
    dados_json = gera_dados_json(resultado_comparacao)
    publica_dados(dados_json)
    exclui_imagem_colecao(faceid_detectadas)
    print(json.dumps(dados_json, indent=4))

main(1,1)