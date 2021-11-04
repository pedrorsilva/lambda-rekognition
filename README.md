Exemplo AWS Lambda + Rekognition | Python Code
Projeto de exemplo com lambda no AWS e Rekognition.

Como definição do Lambda conforme descrito no site da Amazon: O AWS Lambda é um serviço de computação sem servidor e orientado a eventos que permite executar código para praticamente qualquer tipo de aplicação ou serviço de backend sem provisionar ou gerenciar servidores. Você pode acionar o Lambda a partir de mais de 200 serviços da AWS e aplicações de software como serviço (SaaS) e pagar apenas pelo que usar.

Desta forma este projeto é um exemplo simples para testar e verificar o funcionamento do Lambda e atrelando a isso o funcionamento do Rekognition que é uma API que automatiza a análise de imagens e vídeos com machine learning e tem um funcionamento excelente. Execute o projeto e faça alterações para verificar os benefícios destes serviços oferecidos pela Amazon, cabendo ressaltar que da forma que este exemplo foi desenvolvido não existem custos para testes se sua conta ainda estiver no período gratuito conforme regras da AWS.

Orientações
Observação: Os buckets e a função lambda devem estar na mesma região.
Criar os seguintes buckets através de (AWS S3)(https://console.aws.amazon.com/s3/home?region=us-east-1) (escolha a região conforme preferir - exemplo está setado para us-east-1).

Bucket Frontend (AWS S3):
Novo bucket > Nome do bucket: frontend-rekognition (caso utilize outro nome, altere o arquivo /js/importa-dados.js)
Desativar a opção Bloquear todo o acesso público
Criar Bucket
Acesse o bucket
Acesse a tela de permissões e insira o seguinte json em Política do Bucket:
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
Salvar alterações
Em Compartilhamento de recursos de origem cruzada (CORS) insira o json a seguir:
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
Salvar alterações
Acesse Propriedades do Bucket e em Hospedagem de site estático clique em Editar e selecione Ativar > Hospedar um site estático > Documento de índice: "index.html" > Salvar alterações
Na pasta que o código do site estiver aplique o seguinte comando (caso tenha dúvidas sobre como configurar o AWS CLI veja este conteúdo Documentação CLI
aws s3 sync . s3://<nome-bucket-frontend>

Em Propriedades > Hospedagem de site estático agora possuirá um dns para acesso do site, pegue este link e tente acessá-lo para verificação do funcionamento. (Acesse somente para verificar se funcionou, pois o processo não foi finalizando ainda. A seguir será feito o processo para funcionamento do código para reconhecimento das faces.
Bucket Imagens modelo para reconhecimento facial com Rekognition (AWS S3):
Criar bucket > Nome do Bucket: facial-recognition (caso utilize outro nome, altere o arquivo constants.py)
Desativar a opção Bloquear todo o acesso público
Criar Bucket
Acesse o bucket
Acesse a tela de permissões e insira o seguinte json em Política do Bucket:
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
Enviar as imagens das faces que serão reconhecidas para posteriores análises (imagens usadas são somente exemplos, insira as imagens que preferir):
$ cd imagens
$ aws s3 sync . s3://<nome-bucket-imagens-padrao-reconhecimento>
$ cd ..
$ python index.py
Para verificar o funcionamento do reconhecimento, insira o comando a seguir para ver as faces reconhecidas (o código está inserindo como nome reconhecido o nome do arquivo.
aws rekognition list-faces --collection-id <CollectionId> | grep ExternalImageId

Antes de criar a função lambda execute o código face-analise.py para verificar o funcionamento: (A imagem _analise.jpg pode ser qualquer imagem que você quiser que seja analisada)
$ aws s3 cp _analise.jpg s3://<nome-bucket-imagens-padrao-reconhecimento>
$ python face-analise.py
Será exibido as faces reconhecidas conforme imagens de exemplo enviadas
Lambda reconhecimento facial (AWS Lambda)
Agora será criado a função lambda para automatizar este reconhecimento sempre que uma nova imagem _analise.jpg for enviada

Acesse o AWS Lambda e clique em Criar função
Selecione Criar do zero
Nome da função: facial-recognition
Tempo de execução: Python 3.8
Criar função
Altere o nome do arquivo lambda_function.py se quiser, lembrando posteriormente de editar as propriedades em Configurações de tempo de execução em manipulador para <nome_da_função_lambda>.<nome_do_handler_que_no_nosso_caso_será_main>
Existem duas formas de inserir o código, sendo uma delas pelo AWS CLI zipando o código, mas aqui faremos copia e cola do código do arquivo face-analise.py e criaremos um novo arquivo constants.py e colocaremos as constantes do projeto lá.
Clique em Deploy
Abra o AWS IAM > Clique em Funções > Escolha a função que você criou > Clique em Anexar políticas > Em pesquisar digite AmazonRekognitionFullAccess e a selecione, posteriormente procure por AmazonS3FullAccess e também selecione esta permissão > Clique em Anexar política
Volte para a função Lambda
Clicando em Test insira um nome para o evento e coloque este JSON:
{}

Verifique se o teste passou
Clique em Adicionar gatilho
Selecione S3 > Bucket: selecione o seu bucket que contém as imagens com as faces e o arquivo _analise.jpg > Campo Sufixo - opcional: _analise.jpg > Clique em Adicionar
Agora encontre outras imagens que contenham algumas das faces que você inseriu como modelos e envie para o bucket de imagens com o nome _analise.jpg, assim toda vez que uma nova imagem com este nome for adicionada a função será executada e você poderá atualizar o frontend e ver quais faces foram reconhecidas.
Para enviar pelo AWS CLI uma nova imagem _analise.jpg execute o seguinte comando:
aws s3 cp _analise.jpg s3://<nome-bucket-imagens-padrao-reconhecimento>

Atualize a página do frontend, se tudo tiver funcionado ela estará com as novas faces reconhecidas
