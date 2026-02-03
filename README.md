# Teste Técnico - Monitoramento de Operadoras ANS

Solução fullstack para automação de coleta (ETL), armazenamento e visualização de dados contábeis e cadastrais de operadoras de planos de saúde, utilizando dados abertos da ANS.

---

## 🛠️ Tecnologias utilizadas e Decisões técnicas

### 1. Linguagem: Python 🐍

**Escolha:** Para iniciar o projeto, foi pedido para escolher uma entre duas linguagens de programação: Python e Java.
**Justificativa:** Devido a sua flexibilidade, agilidade e facilidade, não só pela escrita do código, mas também pela integração com o FRONTEND e sua proficiência em lidar com arquivos (leitura, download, criação), especialmente arquivos com extensão csv, por haver bibliotecas como o pandas e sqlAlchemy que facilitem essa leitura e também integração direta com banco de dados.

### 2. Banco de dados: PostgreSQL 🐘

**Escolha:** O segundo passo antes de iniciar o projeto foi escolher qual software SQL seria usado para trabalhar com banco de dados.
**Justificativa:** Optei pelo PostgreSQL devido à sua robustez, conformidade com ACID e familiaridade prévia. Ele lida excelentemente com integridade referencial, o que é crucial para relacionar as tabelas de `Operadoras` e `Despesas`. Ademais, com prévias experiências com o PostgreSQL e seu software já instalado na máquina local, isso deixou a escolha ainda mais óbvia.

### 3. Arquitetura do código

**Escolha:** Códigos separados por funcionalidade e Backend separado do Frontend.
**Justificativa:** No Backend foram separados de tal forma que cada arquivo fosse uma etapa do processo de desenvolvimento, nomeados como etapa1, etapa2 e etapa3. Ademais, cada arquivo possui arquitetura de código limpo: funcionalidades únicas por função. No frontend os componentes foram dividos entre componente principal e página de detalhes, garantindo melhor organização do código e facilidade com rotas. Por fim, a separação entre Backend e Frontend garante que o sistema seja escalável e que o processamento de dados (pesado) não impacte a experiência do usuário na interface.

---

## 📋 Pré-requisitos

Para executar este projeto, será necessário:

- **Python 3.10+**
- **Node.js** (v16 ou superior) & **npm**
- **PostgreSQL** (Instalado e rodando na porta 5432)

---

## 🚀 Guia de instalação e configuração

Siga os passos abaixo na ordem apresentada para configurar o ambiente.

### 1. Configuração do Backend

1.  Acesse a pasta do backend:

    ```bash
    cd backend
    ```

2.  Crie um ambiente virtual:

    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate
    ```

3.  Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Variáveis de ambiente (.env):**
    - Renomeie o arquivo `.env.example` para `.env`.
    - Edite o arquivo `.env` e coloque o usuário e senha do **seu** banco de dados PostgreSQL local e o nome do banco de dados criado na variável `DATABASE_URL`.

### 2. Configuração do Banco de dados

1.  Abra seu gerenciador de banco (pgAdmin, DBeaver ou terminal).
2.  Crie um banco de dados vazio chamado: **`datas_info`**.
    - _O script Python criará as tabelas automaticamente, não precisa criar tabelas manualmente._

### 3. Configuração do Frontend

1.  Em um novo terminal, acesse a pasta do frontend:
    ```bash
    cd frontend
    ```
2.  Instale as dependências e configure o ambiente:
    ```bash
    npm install
    ```
    Renomeie o arquivo `.env.example` para `.env`.

---

## ▶️ Como Executar os códigos

Execute os scripts Python na ordem abaixo para realizar o processo completo de ETL (Extract, Transform, Load).
**⚠️ ATENÇÃO:** Antes de executar os códigos, verifique no terminal se o código está sendo executado dentro da pasta **backend** e se o **venv** está ativado (passos 1 a 4).

### Passo 1: Automação de download

Este script conecta no FTP da ANS e baixa os arquivos ZIP (Demonstrações Contábeis) e CSV (Relatório_cadop) automaticamente.

```bash
python script_download.py
```

##### Resultado: Cria a pasta ./assets com os arquivos brutos (zip e csv).

### Passo 2: Extração e tratamento de dados

Extrai os ZIPs, filtra as despesas de "Eventos/Sinistros", limpa os dados e consolida em um único CSV (consolidado_despesas) e joga esses arquivos numa pasta ./files que será criada.

```bash
python etapa1_process_file.py
```

##### Resultado: Cria a pasta ./files com os arquivos unzipados e o arquivo consolidado_despesas.csv e o zip dele.

### Passo 3: Validação de dados e merge de CSVs

Lê o arquivo Relatório_cadop.csv, valida dados: cnpj, razão social vazia e números negativos. Cria um arquivo despesas_agregadas com informações de cada operadora total de despesas + o desafio adicional: média por trimestre e desvio padrão. Por fim faz o merge entre o arquivo consolidado_despesas.csv e o Relatorio_cadop.csv.

```bash
python etapa2_validatingData.py
```

##### Resultado: Cria o arquivo despesas_agregadas.csv com as informações de valores de cada operadora e o arquivo relatorio_final.csv com o merge entre consolidado_despesas.csv + Relatorio_cadop.csv, além de o zip do despesas_agregadas.csv chamado Teste_Gustavo_Luiz.zip, como pedido.

### Passo 4: Popular Banco de dados

Lê os arquivos processados, inicia o banco de dados PostgreSQL, cria as tabelas e popula as tabelas no PostgreSQL. Por fim, cria as 3 queries pedidas:

1. Quais as 5 operadoras com maior crescimento percentual de despesas entre o primeiro e o último trimestre analisado? + desafio.

2. Qual a distribuição de despesas por UF? Liste os 5 estados com maiores despesas totais + desafio adicional.

3. Quantas operadoras tiveram despesas acima da média geral em pelo menos 2 dos 3 trimestres analisados? + trade-off.

```bash
python etapa3_integratingDB.py
```

##### Resultado: Tabelas populadas no banco datas_info, além de retornar a resposta para as três queries pedidas.

### Passo 5: Iniciar a API (Backend)

```bash
uvicorn main:app --reload
```

**Acesse a documentação automática (Swagger) em: http://localhost:8000/docs**

### Passo 6: Iniciar o dashboard (Frontend)

```bash
npm run dev
```

**Acesse a aplicação em: http://localhost:5173**

---

## 📚 Documentação da API

Conforme solicitado, foi criada uma coleção do Postman contendo todas as rotas e exemplos de respostas.

- **Arquivo:** `./postman_collection.json` (Na raíz do projeto)
- **Como usar:** Importe este arquivo no seu Postman para testar as rotas pré-configuradas.
- **Alternativa:** A documentação também está disponível via Swagger em `http://localhost:8000/docs`.

---

## ⚖️ Trade-offs e decisões técnicas

A seguir, segue as justificativas por cada decisão tomada nos trade-offs. Cada um enumerada de acordo com o item a que ela pertence.

##### Observação. Para a manipulação dos arquivos csv eu utilizei a biblioteca Pandas. Embora fosse possível utilizar apenas as ferramentas nativas do Python (csv module), a escolha pelo Pandas se justifica pela praticidade e eficiência (princípio KISS solicitado no teste). O Pandas oferece performance superior no processamento de grandes volumes de dados e reduz drasticamente a complexidade do código para normalização e filtragem, facilitando a manutenção futura. Além de sua forte integridade com a ORM SQLAlchemy que possibilita de forma mais fácil e rápida o transporte de informações do arquivo csv para o Banco de dados.

### Item 1: TESTE DE INTEGRAÇÃO COM API PÚBLICA

#### 1 -> 1.2. Processamento de Arquivos

- Para o processamento de arquivos, a segunda opção (processar incrementalmente) foi a mais viável. Pois, evita carregar todos os arquivos dos dados trimestrais na memória simultaneamente e causar um uso extremo de memória que pode acabar crashando o servidor, dependendo da quantidade de memória RAM que o usuário tem disponível e se o número de dados aumentar posteriormente. Logo, o script itera arquivo por arquivo, extrai apenas os dados desejados (Eventos/Sinistros) guarda o resultado em um arquivo e o restante é passado em branco pelo script.
  - **Vantagem:** Leve e rápido.
  - **Desvantagem:** A escrita código pode ser mais trabalhosa.

##### Observação: Os arquivos fornecidos estão apenas em pdf, porém o código já possui estrutura para adicionar leitores de XLSX e TXT posteriormente.

#### 1 -> 1.3. Consolidação e Análise de Inconsistências

- Nesse item foi solicitado a análise crítica de inconsistências em CNPJs. Porém, foi notório que o arquivo com os dados iniciais ("Demonstrações Contábeis") utiliza apenas o identificador REG_ANS (Registro ANS) e não contém os campos CNPJ ou Razão Social. Dessa forma, mantive a estrutura solicitada preenchida com valores nulos nesta etapa e deixei a validação de CNPJ para a etapa 2.1, onde será feito o enriquecimento com a o relatório cadop. A análise de duplicidade foi feita com base no REG_ANS."
  - **Decisão:** Optei por estruturar o CSV com as colunas solicitadas, mas mantive o campo RegistroANS (chave primária original) e deixei CNPJ/RazaoSocial como espaços vazios. Esses dados serão preenchidos corretamente na etapa 2.2 através do enriquecimento de dados (JOIN com o relatório cadop), garantindo a integridade da informação sem inventar dados na etapa de extração."

### Item 2: TESTE DE TRANSFORMAÇÃO E VALIDAÇÃO DE DADOS

#### 2 -> 2.1. Validação de Dados com Estratégias Diferentes

- O item solicitava a validação de CNPJ no arquivo consolidado. Como este arquivo não possuía a informação originalmente, realizei primeiramente o enriquecimento dos dados (Passo 2.2) para obter os CNPJs e, posteriormente, apliquei a validação de formato e dígitos verificadores conforme solicitado.
  Feito isso, foi possível decidir como tratar CNPJs inválidos: adotei uma estratégia de Auditoria (Non-destructive cleaning). Em vez de excluir registros com CNPJs inválidos, Razão Social vazia ou valores negativos, optei por criar uma coluna de metadados chamada Status_Validacao responsável por **marcar** cada registro, a fim de permitir identificação de inconsistências. Pois, em sistemas financeiros e contábeis, a exclusão silenciosa de registros problemáticos pode gerar divergências nos balanços finais (perda de rastreabilidade do valor total).
  - **Como foi implementado:** Registros corretos recebem a flag "Válido", enquanto registros inválidos recebem a flag "Inválido" com o motivo detalhado (ex: "CNPJ Inválido", "Valor Negativo"). Para a geração do relatório de despesas (despesas_agregadas.csv), utilizei apenas os dados com status "Válido" para garantir a integridade das estatísticas, mas sem excluir os inconsistentes para não perder valores importantes.

#### 2 -> 2.2. Enriquecimento de Dados com Tratamento de Falhas

- O item 2.2 instrui realizar o join utilizando o CNPJ como chave. Contudo, devido à ausência dessa informação no arquivo primário (Demonstrações Contábeis), utilizei o campo RegistroANS (presente em ambas as bases) como chave (key), garantindo a integridade do cruzamento e permitindo a correta importação dos dados de CNPJ, Razão Social, UF e Modalidade.

- Para responder o trade-off técnico, optei pela utilização do **Left Join** (mantendo a base de Despesas como _Left_).
  - **Justificativa:** A prioridade do projeto é a integridade contábil. Utilizar um `Inner Join` descartaria automaticamente despesas de operadoras que não constam no arquivo de "Operadoras Ativas" (ex: empresas canceladas, em liquidação ou com divergência cadastral), gerando um balanço financeiro incompleto.
  - **Resultado:** Todas as despesas foram preservadas. Registros sem correspondência no cadastro tiveram os campos de identificação (CNPJ, Razão Social) preenchidos como nulos para posterior auditoria.

- Durante o desenvolvimento do código, foi identificada a existência de **Registros Órfãos** (operadoras com lançamentos de despesas, mas ausentes no arquivo de cadastro de ativas (cadop)), o que gerava incompatibilidade ao fazer o JOIN, pois é como se houvesse "operadoras fantasmas". É possível enxergar com mais detalhes no console ao executar o arquivo `etapa2_validatingData.py`.
  - **Tratamento:** Esses registros **não foram excluídos**. Foram mantidos no dataset final para garantir que o valor total das despesas (soma) bata com a origem, mas receberam flag de validação correspondente.

- Para a parte de validação de dados proposta anteriormente nos items 1.3 e 2.1 foi implementada uma rotina de validação (`general_validation`), gerando a coluna de metadados `Status_Validacao`, já citada anteriormente no item 2.1. As regras aplicadas foram:
  1. **Validação de CNPJ:** Verificação de formato (14 dígitos) e cálculo matemático dos Dígitos Verificadores (Módulo 11).
  2. **Validação de Valores:** Flag em despesas com valor negativo.
  3. **Dado vazio:** Verificação de Razão Social vazia ou nula.

#### 2 -> 2.3. Agregação com Múltiplas Estratégias

- Para a ordenação preferi escolher o método sort_values, realizada em memória via Pandas antes da exportação para CSV. Pois, dado o volume de dados processado, o custo computacional de ordenar em memória é desprezível se comparado ao benefício de entregar um relatório já priorizado para o usuário final, facilitando a identificação imediata das maiores despesas sem necessidade de pós-processamento em ferramentas como Excel. Se estivéssemos lidando com Big Data, a ordenação seria postergada para a camada de visualização para economizar recursos de processamento distribuído.

### Item 3: TESTE DE BANCO DE DADOS E ANÁLISE

#### 3 -> 3.2. Crie queries DDL para estruturar as tabelas necessárias:

- Optei pela Opção B: criar tabelas normalizadas separadas para Agregados, Operadoras e Despesas, ligadas por chave estrangeira (registro_ans). Pois, a normalização evita redundância de dados cadastrais (ex: repetir a Razão Social milhares de vezes na tabela de despesas), economizando armazenamento e facilitando atualizações cadastrais (basta alterar em um lugar).

- Para os tipos de dados, eu escolhi o DECIMAL, (NUMERIC no SQLAlchemy) para numéricos e DATE para datas.
  - **Numérico:** Utilizar o tipo INTEGER é inviável nesse sentido, uma vez que estamos trabalhando com valores monetários, que podem vim quebrados por centavos. Entre o FLOAT e DECIMAL, o FLOAT não é o melhor, pois ele tem problemas com o ponto flutuente, podendo fazer arredondamentos equivocados, logo, o DECIMAL se sobressai.
  - **Data:** Quando as datas são importante para um registro (como é o nosso caso), o VARCHAR não é recomendado pois ele armazena datas como string, e isso impossibilita operações diretas com as datas, pois eu teria que fazer um processo para converter o tipo texto para DATE posteriormente. O timestamp armazena data e hora, nos registros, as informações de data continham apenas data, sem hora. Por isso, o DATE é o melhor por armazenar apenas o que queremos que é o que é entregue pelos registros.

#### 3 -> 3.3. Elabore queries para importar o conteúdo dos arquivos CSV:

- Realizando a análise crítica durante a importação dos dados dos arquivos csv:
  - **Valores NULL em campos obrigatórios:** Implementei um filtro (dropna) para descartar registros de operadoras que não possuíssem CNPJ ou Razão Social, garantindo a integridade da constraint NOT NULL do banco de dados.
  - **Strings em campos numéricos:** Utilizei o parâmetro decimal="," na leitura do Pandas para interpretar corretamente o formato brasileiro de moeda, convertendo strings numéricas para float antes da inserção.
  - **Datas em formatos inconsistentes:** Apliquei pd.to_datetime(..., errors='coerce'). Datas inválidas foram convertidas para NULL (permitido na modelagem), preservando o registro em vez de descartá-lo, mas mantendo a consistência do tipo de dado DATE.

#### 3 -> 3.4. Desenvolva queries analíticas para responder:

- Explicando o trade-off da Query 1: Para o cálculo de crescimento, utilizei um INNER JOIN entre os dados do primeiro e do último trimestre. Isso filtra automaticamente operadoras que não possuem dados em um dos dois períodos. Essa abordagem foi escolhida porque, matematicamente, não é possível calcular a taxa de crescimento se o valor inicial for inexistente (nulo) ou zero (o que causaria erro de divisão por zero). Portanto, apenas operadoras com atividade contínua no período analisado foram consideradas.

- Explicando o trade-off da Query 3: Optei pela abordagem utilizando CTEs (Common Table Expressions) (WITH media_global AS...) em vez de Subqueries aninhadas no WHERE ou JOINs complexos. Pois, melhora a legibilidade do código, tendo um passo-à-passo de como cada linha se comporta até o resultado final. Melhora a manutenibilidade do código, visto que evita alterar toda a query sql. Basta apenas alterar alguma CTE conforme o que for pedido.

### Item 4: TESTE DE API E INTERFACE WEB

#### 4 -> 4.2.1. Escolha do Framework:

- Para o Framework utilizado na criação da API, foi escolhido a Opção B: **FastAPI**. Devido sua alta performance, visto que tem um padrão assíncrono já nativo, utiliza tipagem nativa o que torna mais fácil e seguro a validação de dados e possui geração automática de documentação (Swagger UI), agilizando os teste com as rotas da API, tornando a manutenção mais rápida e tirando a necessidade do uso do Postman.

#### 4 -> 4.2.2. Estratégia de Paginação:

- Estratégia de Paginação Escolhida: Opção A: **Offset-based**. É o método padrão utilizado na maioria das APIs REST, por lidar com (LIMIT/OFFSET), facilitando integração com o frontend que apenas recebe os parâmetros page e limit e facilita a UX. Além disso, como não há uma quantidade brutal de dados, não se faz necessário o uso de alguma abordagem mais complexa como o Cursor-based. Portanto, o Offset-based é o mais simples e intuitivo diariamente e para um projeto assim com quantidade de dados razoáveis, mas não extravagantes demais.

#### 4 -> 4.2.3. Cache vs Queries Diretas:

- Estratégia Escolhida: Opção A: **Calcular sempre na hora**. Pois, dado o tamanho do projeto e o volume de dados ser controlado (não ser tão exorbitante), optei por calcular sempre na hora utilizando queries de agregação (SUM, AVG) diretamente na query SQL no Banco de dados. Assim, possibilitando simplicidade, visto que reduz a complexidade da arquitetura sem introduzir componentes extras como Redis ou tabelas temporárias e garantindo que o dado exibido é sempre o dado real do momento, sem risco de cache antigo.

##### Observação: Em um cenário de produção com milhões de acessos, eu migraria para a Opção B (Cachear resultado por X minutos), utilizando o Redis com um tempo de 10 a 60 minutos.

#### 4 -> 4.2.4. Estrutura de Resposta da API:

- Estrutura de Resposta da API: Opção B: **Dados + Metadados**. O uso de dados + metadados é mais interessante para projetos que contenham um Dashboard, como este. Pois, eles possuem registros com alto número de dados, o que impossibilita o retorno somente dos dados, pois sem controle de páginas e com muitos dados, o Frontend teria uma tabela com scroll infinito, o que quebra a UX. Portanto, ao retornar os metadados o Frontend pode ter controle das páginas e retornar somente o número correto de dados por página (baseado no LIMIT/OFFSET). Assim, permite uma UI melhor de paginação, mostrar a página que o usuário está dentre a quantidade de páginas existentes, assim melhorando a UX.

#### 4 -> 4.3.1. Estratégia de Busca/Filtro:

- Estratégia de Busca/Filtro: Opção A: **Busca no Servidor**. Pois,
  - **Volume de Dados e Escalabilidade:** O cadastro de operadoras da ANS e seus dados históricos representam um conjunto de dados potencialmente grande e em crescimento contínuo. Carregar todos os registros para o navegador do cliente (Client-side) de uma única vez resultaria em um payload inicial muito pesado, aumentando drasticamente o tempo de carregamento da aplicação e consumindo memória excessiva do dispositivo do usuário. A busca no servidor garante que o frontend receba apenas o subconjunto de dados preciso, mantendo a aplicação leve e performática independente do tamanho total do banco de dados.
  - **Experiência do Usuário (UX):** Embora a busca no servidor introduza uma latência de rede a cada requisição, ela evita o travamento da interface que ocorreria ao tentar filtrar arrays com milhares de objetos via JavaScript no navegador. Utilizando eventos como @change, garantimos que o usuário tenha uma resposta precisa e atualizada diretamente da fonte da verdade (banco de dados), sem riscos de dados obsoletos em cache local.

#### 4 -> 4.3.2. Gerenciamento de Estado:

- Para gerenciar os dados das operadoras: Opção C: **Composables (Vue 3)**. Pois,
  - **Complexidade da Aplicação:** O escopo atual da aplicação foca em um dashboard onde os dados são consumidos e exibidos no mesmo componente, componente específico para mostrar os dados, logo, não há necessidade de compartilhar a lista de operadoras com outros componentes distantes na árvore da aplicação (como um rodapé, sidebar ou carrinho de compras), o que torna o uso de uma biblioteca de gerenciamento global (como Pinia ou Vuex) uma complexidade desnecessária.
  - **Manutenibilidade e Simplicidade:** A simplicidade que o uso do Reactivity API (ref) junto com os componentes de renderização (onMounted, onUpdated) é um estratégia simples, porém muito forte. O ref consegue gerenciar estados perfeitamente, e, caso a aplicação cresça no futuro, a lógica de refs pode ser extraída para Composables reutilizáveis, tornando essa ideia ainda mais forte.

#### 4 -> 4.3.3. Performance da Tabela:

- Para exibir muitas operadoras, a estratégia utilizada foi a renderização padrão com paginação no servidor. Pois,
  - **Volume de Dados:** Embora o banco de dados possa conter milhares de registros, a aplicação nunca renderiza todos de uma vez. Ao limitar a resposta a 10 itens por página (devido ao LIMIT no backend), o número de nós no DOM (Document Object Model) permanece constante e baixo. Isso torna desnecessário o uso de técnicas complexas como virtualização, que só se justificariam se precisássemos exibir centenas de linhas simultaneamente na mesma tela.
  - **Requisitos de UX:** A paginação tradicional oferece uma navegação previsível e permite que o usuário tenha uma noção clara de "onde está" (Ex: Página 2 de 50). A renderização padrão do Vue.js é extremamente eficiente para listas pequenas, garantindo transições de página instantâneas e baixo consumo de memória no navegador do cliente, mesmo em dispositivos móveis.

#### 4 -> 4.3.4. Tratamento de Erros e Loading:

- Como eu trato erros e loading:
  - **Erros de Rede/API:** Implementado através de blocos try/catch na função assíncrona, como na função loadOperators. Em caso de falha, o erro é capturado e logado no console para depuração (console.error). Para evitar que a interface dê um crash, o estado é resetado para uma lista vazia, garantindo que a aplicação continue funcional mesmo sem dados.
  - **Estados de Loading:** É utilizado renderização condiciona do Vue.js (v-if/v-else). Enquanto a variável que armazena os dados é null, um spinner centralizado é exibido. Isso previne uma mudança brusca de layout, quebrando a UX e informa visualmente ao usuário que o sistema está processando a requisição. Assim, a interface de dados só é montada após a resposta completa da API.
  - **Dados Vazios (Empty State):** Verificação explícita do tamanho do array (ex: operatorsData.operators.length === 0). Caso a busca retorne sucesso (200 OK) mas sem resultados, exibe-se uma mensagem amigável ("Nenhuma operadora encontrada...") em vez de uma tabela vazia com cabeçalhos órfãos, melhorando a clareza para o usuário. Esse comportamento evita o uso do status 404 no backend e o eventual crash no frontend.

- Análise crítica (mensagens genéricas ou específicas): Utilizei uma abordagem híbrida (feedback específico para contexto, mas genérico para erros de sistema). Quando o frontend realiza uma requisição e não retorna dados ou dá algum erro, mostramos o que aconteceu, uma mensagem específica, como é o caso da mensagem "Nenhuma operadora encontrada...". Para erros de sistema, evitamos mostrar os erros reais, pois o usuário pode não entender algum erro dentro do servidor, por exemplo, e isso pode ser um problema. Por isso apenas mostra uma mensagem genérica de erro.

---

## 🌟 Diferenciais Implementados

- **🤖 Automação Completa:** Scripts de download e ETL resilientes que eliminam intervenção manual.
- **⚡ Performance:** Uso de streaming para downloads e leituras otimizadas com Pandas.
- **📝 ORM - Banco de dados:** Uso do ORM SQLAlchemy para facilitar a criação das tabelas no banco de dados, tornando o processo mais eficiente e aumentando a performance, devido a integração do SQLAlchemy com o Pandas.
- **📊 Nova rota "/api/operadoras/{cnpj}/despesas/chart":** Rota que leva os dados para popular o gráfico na página de detalhes com as despesas de cada trimestre da operadora.
- **📊 Visualização Rica:** Frontend interativo com gráficos (Chart.js) e tratamento de erros de UX.
- **📊 Visualização top 5 maiores despesas:** Seção com o ranking das 5 operadoras com mais despesas.
- **📝 Documentação Viva:** Uso do Swagger UI para documentação interativa da API.
- **🗂️ Versionamento:** Histórico Git estruturado.

---

Agradeço a oportunidade de participar desse projeto. Foi uma experiência incrível.

- **Autor:** Gustavo Luiz Scobernatti de Almeida.
- **Links importantes para contato:**
  - **Github:** https://github.com/GuScobernatti
  - **LinkedIn:** https://www.linkedin.com/in/gustavo-scobernatti/
  - **WhatsApp:** 33984630077
