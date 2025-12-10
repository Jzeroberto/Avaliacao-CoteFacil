# Avaliação CoteFácil

Este repositório contém a solução desenvolvida para o projeto **Avaliação CoteFácil**, utilizando **Python**, **Scrapy**, **Requests** e **Selenium**, além de um ambiente totalmente executável via **Docker**.

## 🐍 Bibliotecas Utilizadas

### **Requests**

A biblioteca **Requests** permite fazer requisições HTTP de forma simples e direta. É ideal para consumir APIs REST, baixar conteúdo de páginas e enviar formulários.

Principais usos no projeto:

* Realizar requisições GET/POST para APIs.
* Obter dados estruturados em JSON.
* Testar endpoints rapidamente.

---

### **Scrapy**

Scrapy é um framework poderoso para **web scraping** e **extração de dados**.

Principais usos no projeto:

* Criar spiders capazes de navegar entre páginas.
* Coletar textos, links e informações estruturadas.
* Tratar respostas assíncronas e múltiplas páginas.

---

### **Selenium**

Selenium é uma ferramenta de automação de navegadores, permitindo controlar páginas como um usuário real.

Principais usos no projeto:

* Clicar em botões e links.
* Preencher formulários.
* Acessar páginas protegidas com interações dinâmicas.

---

## 🐳 Como executar com Docker

Você pode executar todas as questões do projeto utilizando Docker. Abaixo está um exemplo de uso.

### **1. Build da imagem:**

```bash
docker build -t avaliacao .
```

### **2. Executar uma questão específica:**

```bash
docker run --rm avaliacao q6 "J.K. Rowling"
```

### **3. Executar outra questão (exemplo):**

```bash
docker run --rm avaliacao q2 "parametros aqui"
```

Substitua **q6**, **q2** e os parâmetros conforme o projeto.

---

## 📂 Estrutura do Projeto

*(Adapte depois com sua estrutura real)*

```
/Questao 1
/Questao 2
/Questao 4
/Questao 5
/Questao 6
/Questao 7 
Dockerfile
requirements.txt
README.md
run.py
```

---

## ✨ Observações

* O projeto utiliza Python 3.
* Todas as dependências estão listadas no `requirements.txt`.
* O Docker garante que o ambiente seja executado de forma padronizada.

---

## 📄 Licença

Este projeto é apenas para fins de estudo e avaliação.
