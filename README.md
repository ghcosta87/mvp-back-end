# 🏠 Gestor Residencial MVP

Este projeto é um MVP (Minimum Viable Product) focado na gestão inteligente do lar. A aplicação centraliza o **gerenciamento de rotinas de manutenção da casa** e uma **lista de compras dinâmica**, capaz de registrar e calcular a média de variação de preços dos produtos ao longo do tempo. A interface visual foi construída utilizando **Bootstrap** para garantir responsividade e facilidade de uso.

> **Contexto Acadêmico:** Este projeto faz parte do escopo de avaliação e material didático da disciplina **Desenvolvimento Full Stack Básico**. O objetivo principal é ilustrar e aplicar na prática os conceitos arquiteturais e de código apresentados ao longo das aulas.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python + Flask
* **Frontend:** HTML5, CSS3, Bootstrap
* **Ambiente Isolado:** Virtualenv (`venv`)

---

### Links
No momento da submissão, envie os links abertos (sem hiperlinks embutidos) seguindo o modelo abaixo:

```text
Olá, seguem os dados referentes à entrega do meu MVP.

Link para o vídeo: [https://www.youtube.com/](https://www.youtube.com/)...
Link para o repositório do back-end: [https://github.com/seu-usuario/back-end](https://github.com/seu-usuario/back-end)...
Link para o repositório do front-end: [https://github.com/seu-usuario/front-end](https://github.com/seu-usuario/front-end)...
```

## 🚀 Como executar o projeto na sua máquina
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
flask run --host 0.0.0.0 --port 5000
```
```text
Abra o [http://localhost:5000/#/](http://localhost:5000/#/) no navegador para verificar o status da API em execução.
```

## CONFIGURANDO PARA SELF HOSTING 
```bash
mkdir precohub
cd precohub
git clone https://github.com/ghcosta87/mvp-back-end.git
mv mvp-back-end backend

echo 'API_NAME="Gemini API Key"' > backend/.env
echo 'API_KEY=""' >> backend/.env
echo 'PROJECT_NAME=""' >> backend/.env 
echo 'PROJECT_NUMBER=""' >> backend/.env
nano backend/.env

git clone https://github.com/ghcosta87/mvp-front-end.git
mv mvp-front-end frontend

nano frontend/js/constantes.js

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

echo "services:" > docker-compose.yaml
echo "  api:" >> docker-compose.yaml
echo "    build: ./backend" >> docker-compose.yaml
echo "    ports:" >> docker-compose.yaml
echo "      - "35111:5000"" >> docker-compose.yaml
echo "    restart: unless-stopped" >> docker-compose.yaml
echo "  web:" >> docker-compose.yaml
echo "    build: ./frontend" >> docker-compose.yaml
echo "    ports:" >> docker-compose.yaml
echo "      - "35112:80"" >> docker-compose.yaml
echo "    depends_on:" >> docker-compose.yaml
echo "      - api" >> docker-compose.yaml
echo "    restart: unless-stopped" >> docker-compose.yaml

docker-compose up -d --build
```

## CONFIGURAR API DO GEMINI
1. Acesse o link ()[] 
2. Gere sua chave API
3. Edite o arquivo em backend/.env com as credenciais da API


## COMO ATUALIZAR
Na pasta pasta raiz "precohub":
```bash
docker compose down --rmi all

mv frontend/Dockerfile Dockerfile-frontend
mv backend/Dockerfile Dockerfile-backend
mv backend/.env .env
mv database/db.sqlite3 db.sqlite3

rm -Rf frontend backend

git clone https://github.com/ghcosta87/mvp-back-end.git
mv mvp-back-end backend
mv .env backend/.env

git clone https://github.com/ghcosta87/mvp-front-end.git
mv mvp-front-end frontend
mv Dockerfile-frontend frontend/Dockerfile
mv Dockerfile-backend backend/Dockerfile
mv db.sqlite3 database/db.sqlite3
nano frontend/js/constantes.js

docker compose up -d --build
```
## Histórico de versões:
- [x] Primeira instalação e testes de fucionamento  
- [ ] 
- [ ] 

## BUGS
- [ ] se apagar a base de dados é possivel logar e ver os dados que ficaram salvos
- [ ] cadastro concluido com sucesso está retornando erro no toast
- modal fica aberto na pagina inicial

## FEAT REQUEST
- [ ] botao no alto a direita pra trocar o tema, com apenas um icone
- [ ] adicionar o spinner de loading no botao de cadastro
