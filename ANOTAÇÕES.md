
## O que já foi feito:
- [x] Configuração do Flask e Nginx em containers Docker
- [x] Interface em CSS Grid e Bootstrap
- [ ] Integração de processamento de imagens

| Tecnologia | Função no Projeto |
|---|---|
| Python (Flask) | Backend API |
| SQLite | Banco de Dados |
| Nginx | Servidor Web Frontend |

Configurado a estrutura
```text
meu-mvp/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile       <-- (Configuração do container Python)
│
├── frontend/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── Dockerfile       <-- (Configuração do container Nginx)
│
└── docker-compose.yml   <-- (O maestro que rege os dois)
```

### Docker compose
```text
services:
  api:
    build: ./backend
    ports:
      - "5000:5000"
    restart: unless-stopped
  web:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - api
    restart: unless-stopped
```

### Dockerfile do frontend

### Dockerfile do backend


## ADICIONAR NO README
- comandos do docker
echo "" > docker-compose.yaml; nano docker-compose.yaml; docker-compose up -d --build
docker compose down --rmi all && docker compose up -d --build

- docker files



### Notas de aprendizado ~ Referências
Nota da Documentação:
"Este atributo booleano indica ao navegador que o script deve ser executado após a análise do documento, mas antes do evento DOMContentLoaded ser disparado."
Referência: MDN Web Docs - O elemento Script de Imersão (Atributo defer)


## 📋 Requisitos e Composição da Nota

Este projeto foi desenvolvido para atender aos seguintes critérios avaliativos:

### Back-end e Banco de Dados (4,0 pts)
* A API deve possuir no mínimo 4 rotas implementadas em Python/Flask.
* Pelo menos uma rota deve utilizar o método POST (ex: cadastro).
* Utilização do banco de dados SQLite com pelo menos uma tabela.
* Documentação completa da API utilizando Swagger (OpenAPI) cobrindo rotas, métodos HTTP, requisições, respostas e status esperados.
* Demonstração de criatividade e inovação, indo além do exemplo base.

### Front-end (4,0 pts)
* Desenvolvimento de uma SPA (Single Page Application) com HTML, CSS e JavaScript puro.
* **Restrição importante:** O uso de frameworks SPA como Angular, Vue ou React acarreta penalização de 1,5 pt.
* A interface deve apresentar originalidade visual e exibir os dados (como usuários/itens) em formato de lista ou cards.
* O front-end deve interagir com todas as rotas implementadas na API.
* A aplicação deve rodar corretamente apenas abrindo o arquivo `index.html` no navegador. O uso de servidores locais ou extensões adicionais acarreta penalização de 2,0 pts.

### Organização dos Códigos (2,0 pts)
* Separação em dois projetos distintos com repositórios Git próprios (um para Back-end, outro para Front-end).
* Presença de um arquivo `README.md` formatado e descritivo em ambos os repositórios.
* *Aviso:* O reuso de mais de 50% do código de exemplo apresentado em aula sujeita a entrega a penalizações.

---

## 📹 Sobre a Entrega Final

A entrega do MVP exige a gravação de um vídeo de demonstração e o envio dos links dos repositórios públicos.

### Diretrizes do Vídeo
* **Duração:** O vídeo deve ter **no máximo 4 minutos** (exceder o tempo resulta em desconto de 0,5 pt).
* **Penalidades:** A não entrega do vídeo penaliza a nota em 2,0 pts. A ausência de qualquer um dos tópicos do roteiro gera desconto de até 2,0 pts (0,67 pts por tópico ausente).

### Roteiro Obrigatório
1. **Objetivo da Aplicação (20 a 60 seg):** Explicar o propósito do sistema e qual problema ele resolve.
2. **Execução da API (60 a 90 seg):** Demonstrar a API funcionando e interagindo com as rotas através da interface do Swagger.
3. **Execução do Front-end (60 a 90 seg):** Navegar pela aplicação no browser, demonstrando onde e como cada rota da API é acionada.