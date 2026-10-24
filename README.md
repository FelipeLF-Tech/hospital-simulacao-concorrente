# Hospital — simulação concorrente de recursos

Projeto de Sistemas Operacionais em Python. Cada paciente é um processo; médicos, salas e leitos são recursos compartilhados por filas. Simula consulta, exame, cirurgia opcional e recuperação, gerando relatório de eventos fictícios.

Execute `python simulacao_hospital.py`. Opções: `--pacientes 25`, `--escala-tempo 1`, `--saida relatorio.txt`. Usa biblioteca padrão.

Revisão assistida por IA: recursos liberados em finally, logs consumidos enquanto processos executam, remoção de Queue.empty(), compatibilidade com spawn e nomes de pacientes fictícios. Foram executados 25 pacientes com escala-tempo 0.001, com saída bem-sucedida. A revisão reestruturou o programa original; não foi validado como sistema hospitalar real.
