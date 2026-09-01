# 🏠 Gestor Residencial MVP

Este projeto é um MVP (Minimum Viable Product) focado na gestão inteligente do lar. A aplicação centraliza o **gerenciamento de rotinas de manutenção da casa** e uma **lista de compras dinâmica**, capaz de registrar e calcular a média de variação de preços dos produtos ao longo do tempo. A interface visual foi construída utilizando **Bootstrap** para garantir responsividade e facilidade de uso.

> **Contexto Acadêmico:** Este projeto faz parte do escopo de avaliação e material didático da disciplina **Desenvolvimento Full Stack Básico**. O objetivo principal é ilustrar e aplicar na prática os conceitos arquiteturais e de código apresentados ao longo das aulas.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python + Flask
* **Frontend:** HTML5, CSS3, Bootstrap
* **Ambiente Isolado:** Virtualenv (`venv`)

---

## 🚀 Como executar o projeto na sua máquina

Para rodar esta aplicação, você precisará ter o Python 3 instalado. Siga o passo a passo abaixo no seu terminal para configurar o ambiente e executar a API.

### 1. Preparando o ambiente virtual

É fortemente recomendado o uso de ambientes virtuais para isolar as bibliotecas do projeto e evitar conflitos no seu sistema operacional.

Navegue até o diretório raiz do projeto clonado e crie o ambiente virtual (vamos chamá-lo de `env`):

**No Linux / macOS / WSL:**
```bash
python3 -m venv env
source env/bin/activate
```

### 2. Instalando as dependências e executando a API

```bash
(env)$ pip install -r requirements.txt
(env)$ flask run --host 0.0.0.0 --port 5000
```

Em modo de desenvolvimento é recomendado executar utilizando o parâmetro reload, que reiniciará o servidor automaticamente após uma mudança no código fonte. 

```bash
(env)$ flask run --host 0.0.0.0 --port 5000 --reload
```

Abra o [http://localhost:5000/#/](http://localhost:5000/#/) no navegador para verificar o status da API em execução.

---

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

### Formato de Envio
No momento da submissão, envie os links abertos (sem hiperlinks embutidos) seguindo o modelo abaixo:

```text
Olá, seguem os dados referentes à entrega do meu MVP.

Link para o vídeo: [https://www.youtube.com/](https://www.youtube.com/)...
Link para o repositório do back-end: [https://github.com/seu-usuario/back-end](https://github.com/seu-usuario/back-end)...
Link para o repositório do front-end: [https://github.com/seu-usuario/front-end](https://github.com/seu-usuario/front-end)...
```