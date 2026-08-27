# 🔐 Gerador de Senhas Seguras Web

Uma aplicação web moderna, responsiva e segura criada em **Python (Flask)** para geração de senhas customizadas, contando com critérios de complexidade e medidor de força em tempo real.

<p align="center">
  <img src="./assets/preview.png" alt="Preview do Gerador de Senhas" width="420">
</p>

<p align="center">
  🌐 <b>Acesse a aplicação online:</b> <a href="https://gerador-de-senhas-c1yl.onrender.com" target="_blank">gerador-de-senhas-c1yl.onrender.com</a>
</p>

---

## 🚀 Funcionalidades

- 🎲 **Geração Segura:** Utiliza a biblioteca nativa `secrets` do Python, garantindo aleatoriedade segura para uso criptográfico.
- 🎛️ **Customização Flexível:** Escolha o tamanho exato da senha (6 a 32 caracteres) e combine maiúsculas (A-Z), números (0-9) e símbolos (!@#$).
- 📊 **Medidor de Força em Tempo Real:** Indicador dinâmico em JavaScript que avalia a complexidade (*Fraca*, *Média*, *Forte* e *Impenetrável*).
- 📋 **Cópia para Área de Transferência:** Copie a senha gerada com um clique e receba confirmação visual imediata no ícone.
- 🎨 **Design Moderno:** Interface escura em estilo *Glassmorphism* desenvolvida com Tailwind CSS e ícones do FontAwesome.

---

## 🛠️ Tecnologias Utilizadas

### **Backend**
- **[Python 3](https://www.python.org/):** Linguagem principal do projeto.
- **[Flask](https://flask.palletsprojects.com/):** Microframework web para roteamento e renderização de templates Jinja2.
- **[Gunicorn](https://gunicorn.org/):** Servidor HTTP WSGI para ambiente de produção.

### **Frontend**
- **[HTML5](https://developer.mozilla.org/pt-BR/docs/Web/HTML):** Estrutura da página.
- **[Tailwind CSS](https://tailwindcss.com/):** Framework CSS utilitário (via CDN) para estilização e responsividade.
- **[JavaScript (Vanilla)](https://developer.mozilla.org/pt-BR/docs/Web/JavaScript):** Lógica interativa de atualização do slider, cálculo de força e cópia da senha.
- **[FontAwesome](https://fontawesome.com/):** Ícones vetoriais da interface.

### **Infraestrutura & Dev**
- **[GitHub Codespaces](https://github.com/features/codespaces):** Ambiente de desenvolvimento nuvem baseado em VS Code.
- **[Render](https://render.com/):** Plataforma de hospedagem e deploy contínuo da aplicação web.

---

## 💻 Como Executar o Projeto Localmente

### **Pré-requisitos**
Certifique-se de ter o **Python 3.10+** e o **Git** instalados na sua máquina.

### **Passo a passo**

1. **Clonar o repositório:**
   ```bash
   git clone [https://github.com/thiagoed-souza/gerador-de-senhas.git](https://github.com/thiagoed-souza/gerador-de-senhas.git)
   cd gerador-de-senhas
