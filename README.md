# Exemplo AWS Lambda + Rekognition | Python Code
Projeto de exemplo para os serviços AWS Lambda e Rekognition.

Como definição do [Lambda](https://aws.amazon.com/pt/lambda/) conforme descrito no site da Amazon: *O AWS Lambda é um serviço de computação sem servidor e orientado a eventos que permite executar código para praticamente qualquer tipo de aplicação ou serviço de backend sem provisionar ou gerenciar servidores. Você pode acionar o Lambda a partir de mais de 200 serviços da AWS e aplicações de software como serviço (SaaS) e pagar apenas pelo que usar.*

Desta forma este projeto é um exemplo simples para testar e verificar o funcionamento do Lambda e atrelando a isso o funcionamento do [Rekognition](https://aws.amazon.com/pt/rekognition/) que é uma API que automatiza a análise de imagens e vídeos com machine learning e tem um funcionamento excelente. Execute o projeto e faça alterações para verificar os benefícios destes serviços oferecidos pela Amazon, cabendo ressaltar que da forma que este exemplo foi desenvolvido não existem custos para testes se sua conta ainda estiver no período gratuito conforme regras da AWS.

## Orientações
- Observação: Os buckets e a função lambda devem estar na mesma região.
Criar os seguintes buckets através de [AWS S3](https://console.aws.amazon.com/s3/home?region=us-east-1) (escolha a região conforme preferir - exemplo está setado para us-east-1).

### Bucket Frontend (AWS S3):
1. Novo bucket > Nome do bucket: frontend-rekognition (caso utilize outro nome, altere o arquivo /js/importa-dados.js)
2. Desativar a opção **Bloquear todo o acesso público**
3. **Criar Bucket**
4. Acesse o bucket
5. Acesse a tela de permissões e insira o seguinte json em **Política do Bucket:**

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::<nome-bucket-frontend>/*"
        }
    ]
}
```

6. **Salvar alterações**
7. Em **Compartilhamento de recursos de origem cruzada (CORS)** insira o json a seguir:

```
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": [
            "x-amz-server-side-encryption",
            "x-amz-request-id",
            "x-amz-id-2"
        ],
        "MaxAgeSeconds": 3000
    }
]
```

8. **Salvar alterações**
9. Acesse **Propriedades** do Bucket e em **Hospedagem de site estático** clique em **Editar** e selecione **Ativar** > **Hospedar um site estático** > **Documento de índice:** "index.html" > **Salvar alterações**
10. Na pasta que o código do site estiver aplique o seguinte comando (caso tenha dúvidas sobre como configurar o AWS CLI veja este conteúdo [Documentação CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-options.html)

`$ aws s3 sync . s3://<nome-bucket-frontend>`

11. Em **Propriedades** > **Hospedagem de site estático** agora possuirá um dns para acesso do site, pegue este link e tente acessá-lo para verificação do funcionamento. (Acesse somente para verificar se funcionou, pois o processo não foi finalizando ainda. A seguir será feito o processo para funcionamento do código para reconhecimento das faces.

### Bucket Imagens modelo para reconhecimento facial com Rekognition (AWS S3):
1. **Criar bucket** > Nome do Bucket: facial-recognition (caso utilize outro nome, altere o arquivo constants.py)
2. Desativar a opção **Bloquear todo o acesso público**
3. **Criar Bucket**
4. Acesse o bucket
5. Acesse a tela de permissões e insira o seguinte json em **Política do Bucket:**

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicRead",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::<nome-bucket-imagens-padrao-reconhecimento>/*",
            "Condition": {
                "StringLike": {
                    "aws:Referer": "<link_do_site_estatico>/*"
                }
            }
        }
    ]
}
```

6. Enviar as imagens das faces que serão reconhecidas para posteriores análises (imagens usadas são somente exemplos, insira as imagens que preferir):

```
$ cd imagens
$ aws s3 sync . s3://<nome-bucket-imagens-padrao-reconhecimento>
$ cd ..
$ python index.py
```

7. Para verificar o funcionamento do reconhecimento, insira o comando a seguir para ver as faces reconhecidas (o código está inserindo como nome reconhecido o nome do arquivo.

`$ aws rekognition list-faces --collection-id <CollectionId> | grep ExternalImageId`

8. Antes de criar a função lambda execute o código face-analise.py para verificar o funcionamento: (A imagem *_analise.jpg* pode ser qualquer imagem que você quiser que seja analisada)

```
$ aws s3 cp _analise.jpg s3://<nome-bucket-imagens-padrao-reconhecimento>
$ python face-analise.py
```

9. Será exibido as faces reconhecidas conforme imagens de exemplo enviadas


### Lambda reconhecimento facial (AWS Lambda)

Agora será criado a função lambda para automatizar este reconhecimento sempre que uma nova imagem *_analise.jpg* for enviada

1. Acesse o AWS Lambda e clique em **Criar função**
2. Selecione **Criar do zero**
3. Nome da função: **facial-recognition**
4. Tempo de execução: **Python 3.8**
5. **Criar função**
6. Altere o nome do arquivo lambda_function.py se quiser, lembrando posteriormente de editar as propriedades em **Configurações de tempo de execução** em manipulador para **<nome_da_função_lambda>**.**<nome_do_handler_que_no_nosso_caso_será_main>**
7. Existem duas formas de inserir o código, sendo uma delas pelo AWS CLI zipando o código, mas aqui faremos copia e cola do código do arquivo face-analise.py e criaremos um novo arquivo constants.py e colocaremos as constantes do projeto lá.
8. Clique em **Deploy**
9. Abra o **AWS IAM** > Clique em **Funções** > Escolha a função que você criou > Clique em **Anexar políticas** > Em pesquisar digite **AmazonRekognitionFullAccess** e **AmazonS3FullAccess** selecionando ambas as permissões > Clique em **Anexar política**
10. Volte para a função Lambda
11. Clicando em Test insira um nome para o evento e coloque este JSON:

`{}`

12. Verifique se o teste passou
13. Clique em **Adicionar gatilho**
14. Selecione **S3** > Bucket: selecione o seu bucket que contém as imagens com as faces e o arquivo *_analise.jpg* > Campo Sufixo - opcional: *_analise.jpg* > Clique em **Adicionar**
15. Agora encontre outras imagens que contenham algumas das faces que você inseriu como modelos e envie para o bucket de imagens com o nome *_analise.jpg*, assim toda vez que uma nova imagem com este nome for adicionada a função será executada e você poderá atualizar o frontend e ver quais faces foram reconhecidas.
16. Para enviar pelo AWS CLI uma nova imagem *_analise.jpg* execute o seguinte comando:

`$ aws s3 cp _analise.jpg s3://<nome-bucket-imagens-padrao-reconhecimento>`

17. Atualize a página do frontend, se tudo tiver funcionado ela estará com as novas faces reconhecidas
