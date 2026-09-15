# 🛍️ MVP - Preço Hub - Preços de Supermercado unificados - Backend

Este projeto é um MVP (Minimum Viable Product) com foco no acompanhamento da gestão de preços de itens de Supermercado. A aplicação centraliza armazena dados de produtos, capaz de registrar e calcular a média de variação de preços dos produtos ao longo do tempo.

> **Contexto Acadêmico:** Este projeto faz parte do escopo de avaliação e material didático da disciplina **Desenvolvimento Full Stack Básico**. O objetivo principal é ilustrar e aplicar na prática os conceitos arquiteturais e de código apresentados ao longo das aulas.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python + Flask
* **Frontend:** HTML5, CSS3, Bootstrap
* **Ambiente Isolado:** Virtualenv (`mvp`)

---

## 🔗 Links

### Olá, seguem os dados referentes à entrega do meu MVP.

- Link para o vídeo: [https://www.youtube.com/](https://www.youtube.com/) 
- Link para o repositório do back-end: [https://github.com/seu-usuario/back-end](https://github.com/seu-usuario/back-end)
- Link para o repositório do front-end: [https://github.com/seu-usuario/front-end](https://github.com/seu-usuario/front-end)


## 🚀 Como executar o projeto na sua máquina
### Backend
```bash
git clone https://github.com/ghcosta87/mvp-back-end.git
cd mvp-back-end
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
flask run --host 0.0.0.0 --port 5000
```
Abra o [http://localhost:5000/](http://localhost:5000/) no navegador para verificar o status da API em execução com o Swagger.

### Frontend
```bash
git clone https://github.com/ghcosta87/mvp-front-end.git
```
Abra o arquivo `index.html` com navegador de sua preferência

## 🖥️ CONFIGURANDO PARA SELF HOSTING 
```bash
mkdir precohub
cd precohub
git clone https://github.com/ghcosta87/mvp-back-end.git
mv mvp-back-end backend

git clone https://github.com/ghcosta87/mvp-front-end.git
mv mvp-front-end frontend

echo "FROM python:3.10-slim" > backend/Dockerfile
echo "WORKDIR /app" >> backend/Dockerfile
echo "COPY requirements.txt ." >> backend/Dockerfile 
echo "RUN pip3 install -r requirements.txt" >> backend/Dockerfile
echo "COPY . ." >> backend/Dockerfile
echo "EXPOSE 5000" >> backend/Dockerfile
echo 'CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]' >> backend/Dockerfile

echo "FROM nginx:alpine" > frontend/Dockerfile
echo "COPY . /usr/share/nginx/html" >> frontend/Dockerfile
echo "EXPOSE 80" >> frontend/Dockerfile
nano frontend/js/constantes.js

echo "services:" > docker-compose.yaml
echo "  api:" >> docker-compose.yaml
echo "    build: ./backend" >> docker-compose.yaml
echo "    ports:" >> docker-compose.yaml
echo "      - "35111:5000"" >> docker-compose.yaml
echo "    restart: unless-stopped" >> docker-compose.yaml
echo "    volumes:" >> docker-compose.yaml
echo "      - ./backend/database:/app/database" >> docker-compose.yaml
echo "      - ./backend/.env:/app/.env" >> docker-compose.yaml
echo "  web:" >> docker-compose.yaml
echo "    build: ./frontend" >> docker-compose.yaml
echo "    ports:" >> docker-compose.yaml
echo "      - "35112:80"" >> docker-compose.yaml
echo "    depends_on:" >> docker-compose.yaml
echo "      - api" >> docker-compose.yaml
echo "    restart: unless-stopped" >> docker-compose.yaml

docker compose build

mv frontend/Dockerfile .Dockerfile-frontend
mv backend/Dockerfile .Dockerfile-backend

rm -Rf frontend backend
mkdir backend backend/database

echo 'API_NAME="Gemini API Key"' > backend/.env
echo 'API_KEY=""' >> backend/.env
echo 'PROJECT_NAME=""' >> backend/.env 
echo 'PROJECT_NUMBER=""' >> backend/.env

nano backend/.env

docker compose up -d

```

## 🤖 CONFIGURAR API DO GEMINI
1. Acesse o link ()[] 
2. Gere sua chave API
3. Edite o arquivo em backend/.env com as credenciais da API

## ‼️ COMO ATUALIZAR
Na pasta pasta raiz "precohub":
```bash
docker compose down --rmi all

mv backend/.env .env
mv backend/database/db.sqlite3 db.sqlite3

rm -Rf backend

git clone https://github.com/ghcosta87/mvp-back-end.git
mv mvp-back-end backend
cp .Dockerfile-backend backend/Dockerfile

git clone https://github.com/ghcosta87/mvp-front-end.git
mv mvp-front-end frontend
cp .Dockerfile-backend backend/Dockerfile
nano frontend/js/constantes.js

docker compose build

mv db.sqlite3 backend/database/db.sqlite3
mv .env backend/.env

docker compose up -d

```
## BUGS
- [ ] se apagar a base de dados é possivel logar e ver os dados que ficaram salvos
- [ ] cadastro concluido com sucesso está retornando erro no toast
- [ ] modal fica aberto na pagina inicial
- [ ] algumas vezes o aviso "toast" fica somente em vermelho
- [ ] ao anexar o arquivo o sidebar não esconde
- [ ] avisos do painel nao estao centralizados
- [ ] botao voltar na janela de cadastro esta sem fade ao passar o mouse
- [ ] precisa alterar a resposta para receber o nome do usuário, e não o email
- [ ] precisa rever função "renderizarLista" "filtrarProdutos"
- [ ] preciso entender melhor o filehandler, está muito bagunçado

## FEAT REQUEST
- [ ] botao no alto a direita pra trocar o tema, com apenas um icone
- [ ] adicionar o spinner de loading no botao de cadastro
- [ ] passar texto simulando chat da AI abaixo da barra de pesquisaq
- [ ] criar fila de envio
- [ ] permitir guardar as fotos
- [ ] criar página inicial acima de todas para indicar o carregamento


## CHECKLIST PRE ENTREGA
### Backend
```python
# Testes de POST deletar_usuario
HTTPStatus.OK                     # 200  # ✅
HTTPStatus.BAD_REQUEST            # 400  # 
HTTPStatus.UNAUTHORIZED           # 401  # ✅
HTTPStatus.CONFLICT               # 409  #
HTTPStatus.UNPROCESSABLE_ENTITY   # 422  # 
```
