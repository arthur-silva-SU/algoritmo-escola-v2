import os
import easygui
import rpy2.robjects as ro

from pathlib import Path
from dotenv import load_dotenv
from rpy2.robjects.vectors import StrVector

BASE_DIR = Path(__file__).resolve().parent

load_dotenv()

caminho_dados = easygui.fileopenbox(default=str(os.getenv('DEFAULT_PATH')))
caminho_saida_finais = f"{BASE_DIR}/dados_finais.csv"
caminho_saida_parametros = f"{BASE_DIR}/dados_parametros.csv"
caminho_pacotes_r = str(os.getenv('CAMINHO_PACOTES_R'))

# Pegar o local onde estão instalados os pacotes R necessários para o funcionamento do programa
ro.r('.libPaths')(StrVector([caminho_pacotes_r]))

# Jogar os parâmetros para dentro do código R
ro.r.assign('caminho_dados', caminho_dados)
ro.r.assign('caminho_saida_finais', caminho_saida_finais)
ro.r.assign('caminho_saida_parametros', caminho_saida_parametros)

# Código R com as variáveis criadas em python nos seus devidos locais
r_code = r'''
    # Load packages
    library(mirt)
    library(dplyr)
    library(jsonlite)
    
    # Read student data from JSON file using the R variable
    dados_alunos <- fromJSON(caminho_dados)
    
    # Rest of your R code...
    # Store student names
    nomes_alunos <- dados_alunos$aluno
    
    # Prepare data for IRT analysis
    dados_tri <- as.matrix(dados_alunos[, -1])
    
    # Create 3PL model from response data
    modelo_tri <- mirt(dados_tri, 1, itemtype = "3PL")
    
    # Estimate student abilities (theta)
    fscores_result <- fscores(modelo_tri, full.scores = TRUE)
    if (is.list(fscores_result)) { 
      theta_estimado <- fscores_result$score 
    } else { 
      theta_estimado <- fscores_result 
    }
    
    # Calculate total correct answers for each student
    total_acertos <- rowSums(dados_tri)
    
    # Define desired mean and standard deviation
    media_desejada <- 500
    desvio_padrao_desejado <- 100
    
    # Calculate mean and standard deviation of theta scores
    media_theta <- mean(theta_estimado)
    desvio_padrao_theta <- sd(theta_estimado)
    
    # Perform linear transformation
    score_transformado <- (theta_estimado - media_theta) / desvio_padrao_theta * desvio_padrao_desejado + media_desejada
    
    # Format transformed score
    score_formatado <- format(round(score_transformado, 2), nsmall = 2, decimal.mark = ",")
    
    # Prepare final data
    dados_finais <- data.frame(
        Aluno = nomes_alunos,
        Total_Acertos = total_acertos,
        Score_TRI = theta_estimado,
        Score_ENEM = score_formatado
    )
    
    # Save final data to CSV using the R variable
    write.csv(dados_finais, caminho_saida_finais, row.names = FALSE)
    
    # Question parameters
    parametros_questoes <- coef(modelo_tri, IRTpars = TRUE)
    dados_parametros <- data.frame(Questao = character(0), a = numeric(0), b = numeric(0), g = numeric(0), u = numeric(0))
    nomes_questoes <- names(parametros_questoes)
    
    for (i in seq_along(parametros_questoes)) {
        if (grepl("GroupPars", nomes_questoes[i])) next
        dados_questao <- c(Questao = nomes_questoes[i], as.numeric(parametros_questoes[[i]]))
        dados_parametros <- rbind(dados_parametros, dados_questao)
    }
    
    colnames(dados_parametros)[-1] <- c("a", "b", "g", "u")
    
    dados_parametros$Nível <- cut(
        as.numeric(dados_parametros$b),
        breaks = c(-Inf, -2, -1, 1, 2, Inf),
        labels = c("Muito Fácil", "Fácil", "Médio", "Difícil", "Muito Difícil"),
        include.lowest = TRUE
    )
    
    names(dados_parametros) <- c("questao", "discriminacao", "dificuldade", "adivinhacao", "u", "nivel")
    dados_parametros$questao <- gsub("X\\.", "", dados_parametros$questao)
    dados_parametros <- dados_parametros[!grepl("GroupPars", dados_parametros$questao),]
    
    # Save parameters to CSV using the R variable
    write.csv(dados_parametros, caminho_saida_parametros, row.names = FALSE)
'''

# Executar o código R
ro.r(r_code)
