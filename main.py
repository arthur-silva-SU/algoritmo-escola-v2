
# Importa os módulos do rpy2 para interação com R
import rpy2.robjects as ro


# Você pode executar o código R inteiro via uma string multilinha.

# Definindo os caminhos como variáveis Python
caminho_dados = "/home/tuzin/Downloads/resultados_alunos_call.json"
caminho_saida_finais = "/home/tuzin/Downloads/saidas_escola/dados_finais.csv"
caminho_saida_parametros = "/home/tuzin/Downloads/saidas_escola/dados_parametros.csv"

caminho_pacotes_r = "/home/tuzin/R/x86_64-pc-linux-gnu-library/4.3"
comando_carrega_pacotes_r = r'.libPaths("{{caminho_pacotes_r}}")'.replace("{{caminho_pacotes_r}}", caminho_pacotes_r)

# Adicionar local onde os pacotes do R estão instalados no sistema.
ro.r(comando_carrega_pacotes_r)

# Criando a string R como uma string bruta (r''' ... ''') sem interpolação direta
code_r = r'''
    # Carrega os pacotes
    library(mirt)
    library(dplyr)
    library(jsonlite)
    
    # Lê os dados dos alunos do arquivo JSON
    dados_alunos <- fromJSON("{{caminho_dados}}")
    
    # Armazena os nomes dos alunos
    nomes_alunos <- dados_alunos$aluno
    
    # Preparando os dados para análise TRI (remove a coluna de identificação)
    dados_tri <- as.matrix(dados_alunos[, -1])
    
    # Cria um modelo 3PL a partir dos dados de resposta
    modelo_tri <- mirt(dados_tri, 1, itemtype = "3PL")
    
    # Estima as habilidades (theta) dos alunos
    fscores_result <- fscores(modelo_tri, full.scores = TRUE)
    if (is.list(fscores_result)) { 
      theta_estimado <- fscores_result$score 
    } else { 
      theta_estimado <- fscores_result 
    }
    
    # Calcula o total de acertos para cada aluno
    total_acertos <- rowSums(dados_tri)
    
    # Define a média e o desvio padrão desejados
    media_desejada <- 500
    desvio_padrao_desejado <- 100
    
    # Calcula a média e o desvio padrão dos escores theta
    media_theta <- mean(theta_estimado)
    desvio_padrao_theta <- sd(theta_estimado)
    
    # Realiza a transformação linear
    score_transformado <- (theta_estimado - media_theta) / desvio_padrao_theta * desvio_padrao_desejado + media_desejada
    
    # Formata o score transformado para duas casas decimais com vírgula como separador
    score_formatado <- format(round(score_transformado, 2), nsmall = 2, decimal.mark = ",")
    
    # Preparando os dados finais
    dados_finais <- data.frame(Aluno = nomes_alunos,
                               Total_Acertos = total_acertos,
                               Score_TRI = theta_estimado,
                               Score_ENEM = score_formatado)
    
    # Imprime a tabela final dos alunos
    print(dados_finais)
    
    # Estima os parâmetros das questões
    parametros_questoes <- coef(modelo_tri, IRTpars = TRUE)
    
    # Inicializa um data frame para os parâmetros das questões incluindo o nome da questão
    dados_parametros <- data.frame(Questao = character(0), a = numeric(0), b = numeric(0), g = numeric(0), u = numeric(0))
    
    # Obtém os nomes das questões
    nomes_questoes <- names(parametros_questoes)
    
    # Preenche o data frame com os valores de cada questão e adiciona o nome da questão
    for (i in seq_along(parametros_questoes)) {
      if (grepl("GroupPars", nomes_questoes[i])) next
      dados_questao <- c(Questao = nomes_questoes[i], as.numeric(parametros_questoes[[i]]))
      dados_parametros <- rbind(dados_parametros, dados_questao)
    }
    
    # Define os nomes das colunas do data frame
    colnames(dados_parametros)[-1] <- c("a", "b", "g", "u")
    
    # Classifica as questões em níveis com base na dificuldade estimada
    dados_parametros$Nível <- cut(as.numeric(dados_parametros$b), 
                                  breaks = c(-Inf, -2, -1, 1, 2, Inf), 
                                  labels = c("Muito Fácil", "Fácil", "Médio", "Difícil", "Muito Difícil"), 
                                  include.lowest = TRUE)
    
    # Renomeia as colunas de forma definitiva
    names(dados_parametros) <- c("questao", "discriminacao", "dificuldade", "adivinhacao", "u", "nivel")
    
    # Remove prefixos indesejados no nome da questão
    dados_parametros$questao <- gsub("X\\.", "", dados_parametros$questao)
    
    # Remove a última linha relacionada a 'GroupPars'
    dados_parametros <- dados_parametros[!grepl("GroupPars", dados_parametros$questao),]
    
    # Imprime o data frame com os parâmetros das questões
    print(dados_parametros)
    
    # Salva os data frames em arquivos CSV
    write.csv(dados_finais, "{{caminho_saida_finais}}", row.names = FALSE)
    write.csv(dados_parametros, "{{caminho_saida_parametros}}", row.names = FALSE)
'''

# Substituir os placeholders "{{caminho_dados}}" pelos valores corretos
code_r = code_r.replace("{{caminho_dados}}", caminho_dados)
code_r = code_r.replace("{{caminho_saida_finais}}", caminho_saida_finais)
code_r = code_r.replace("{{caminho_saida_parametros}}", caminho_saida_parametros)

ro.r(code_r)