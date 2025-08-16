# Gerador de Flashcards para Anki
Uma ferramenta que cria automaticamente flashcards para o Anki a partir de documentos PDF. Suporta vários provedores de LLM, como OpenAI, Ollama e OpenRouter.
🚀 Guia Rápido
1. Instalação e Execução
Windows:
code
Bash
run.bat
Mac/Linux:
code
Bash
./run.sh
2. Adicionar Arquivos PDF
Coloque os arquivos PDF na pasta SOURCE_DOCUMENTS.
3. Configuração do LLM
No arquivo .env, configure o provedor de LLM que deseja usar.
📁 Estrutura do Projeto
code
Code
Anki_FlashCard_Generator/
├── src/
│ ├── Config/ # Arquivos de configuração
│ ├── Entity/ # Modelos de dados
│ ├── IService/ # Interfaces de serviço
│ ├── Service/ # Implementações de serviço
│ ├── Utils/ # Funções utilitárias
│ └── main.py # Aplicação principal
├── SOURCE_DOCUMENTS/ # Pasta de entrada para PDFs
├── output/ # Saída dos flashcards gerados
├── logs/ # Arquivos de log
├── backup/ # Arquivos de backup
├── .env.example # Modelo de variáveis de ambiente
├── run.sh # Script de execução para Unix
└── run.bat # Script de execução para Windows
⚙️ Configuração
No arquivo .env, você pode configurar os seguintes itens:
LLM_PROVIDER: O provedor de LLM a ser usado (openai, ollama, openrouter).
CARDS_PER_SECTION: O número de cartões a serem gerados por seção.
MIN_CARD_QUALITY: A pontuação mínima de qualidade do cartão (de 0.0 a 1.0).
Consulte o arquivo .env.example para as configurações específicas de cada provedor.
📊 Formato de Saída
Os flashcards gerados são salvos nos seguintes formatos:
Anki TSV: Pode ser importado diretamente no Anki.
CSV: Pode ser editado em planilhas.
JSON: Pode ser processado de forma programática.
🧪 Testes
Testar a conexão com o LLM:
code
Bash
python test_llm_providers.py
Demonstração com múltiplos provedores:
code
Bash
python demo_multi_provider.py
📜 Licença
Licença MIT
Google Search Suggestions
Display of Search Suggestions is required when using Grounding with Google Search. Learn more
Google logo
