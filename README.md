# 🛍️ MVP - Preço Hub - Preços de Supermercado unificados - Backend

Este projeto é um MVP (Minimum Viable Product) com foco no acompanhamento da gestão de preços de itens de Supermercado. A aplicação centraliza e armazena preços dos produtos, registra e calcula a média de variação de preços dos produtos ao longo do tempo.

> **Contexto Acadêmico:** Este projeto faz parte do escopo de avaliação e material didático da disciplina **Desenvolvimento Full Stack Básico**. O objetivo principal é ilustrar e aplicar na prática os conceitos arquiteturais e de código apresentados ao longo das aulas.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python + Flask
* **Ambiente Isolado:** Virtualenv (`mvp`)



## 🔗 Links

### Olá, seguem os dados referentes à entrega do meu MVP.

- Link para o vídeo: [https://www.youtube.com/](https://www.youtube.com/) 
- Link para o repositório do back-end: [https://github.com/ghcosta87/mvp-back-end.git](https://github.com/ghcosta87/mvp-back-end.git)


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

## 🤖 CONFIGURAR API DO GEMINI
1. Acesse o link [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Gere sua chave API
3. Edite o arquivo em backend/.env com as credenciais da API

## A ESTRUTURA
```
meu-mvp/
│
├── backend/
│   ├── database/
│   ├── logs/
│   ├── model/
│   ├── schemas/
│   ├── service/
│   ├── app.py
│   ├── logger.py
│   ├── README.md
│   ├── requirements.txt
│   └── Dockerfile       <-- (Configuração do container Python)
│
├── frontend/
│   ├── js/
│   ├── styles/
│   ├── index.html
│   └── Dockerfile       <-- (Configuração do container Nginx)
│
└── docker-compose.yml   <-- (O maestro que rege os dois)

```
# ➕ Extras 


## 🖥️ CONFIGURANDO PARA SELF HOSTING 

### Docker compose
```bash
services:
  api:
    build: https://github.com/ghcosta87/mvp-back-end.git#preco-hub-v2-beta
    ports:
      - "35111:5000"
    restart: unless-stopped
    volumes:
      - ./database:/app/database
    environment:
      - API_KEY=YOUR_API_KEY

  web:
    build: https://github.com/ghcosta87/mvp-front-end.git#preco-hub-v2-beta
    ports:
      - "35112:80"
    depends_on:
      - api
    restart: unless-stopped
    environment:
      - HOST_IP=IP_DO_BACKEND
    command: /bin/sh -c "sed -i 's|http://127.0.0.1:5000|'\"$$HOST_IP\"'|g' /usr/share/nginx/html/js/constantes.js && nginx -g 'daemon off;'"
```

Através do navegador de sua preferência digite o ip-da-maquina:35112

## BUGS CONHECIDOS
```
- [        ] se apagar a base de dados é possivel logar e ver os dados que ficaram salvos
- [ SOLVED ] reformular filehandler, está muito bagunçado e duplicado
- [        ] login forçado via console libera função GET para puxar os dados do backend
```

## FUTURAS ATUALIZAÇÕES
```
- [        ] criar fila de envio
- [        ] permitir guardar as fotos
- [        ] juntar produtos identicos com nomes diferentes
- [        ] cadastro manual de produtos
- [        ] envio de informações das lojas
```