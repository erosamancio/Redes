# Protocolo de Transporte Confiável de Dados

## Resumo do Projeto
Este projeto consiste em uma aplicação cliente e servidor feita para garantir a entrega segura de dados usando a rede. A ideia principal é usar o protocolo UDP para enviar as mensagens e construir todas as regras de confiabilidade por conta propria direto na camada de aplicação. Isso significa que nosso codigo vai simular perdas e tratar os erros simulando o funcionamento de redes reais. Na etapa atual o foco é o handshake inicial para definir as regras de envio e tamanhos de janela.

## Documentação e Relatórios
* Documentação Semanal: [clique aqui](https://docs.google.com/document/d/1h0GyiDitP_tE2J1AF2Hjil5RTL5TSDVIJ_s-WghsnpU/edit?tab=t.0)
* Declaração de Uso de IA: [clique aqui](https://docs.google.com/document/d/1pjOHOoKNan6quR6PJvSVl1QKgeuARvsd0Fx1S5Z8UIY/edit?usp=sharing)

## Checklist de Entregas

<details>
  <summary><strong>Entrega 1: Handshake & Sockets (09/09/2026)</strong></summary>

  <br>
  
  * Conexão entre aplicação cliente e servidor via socket ✅
  * Troca de mensagens estabelecendo o modo de operação (individual/lote e Go-Back-N/Repetição Seletiva) ✅
  * Definição dinâmica do tamanho máximo do texto com limite mínimo de 30 caracteres ✅
  * Determinação do tamanho inicial da janela pelo servidor (variando de 1 a 5) ✅
  * Impressão dos metadados das mensagens e confirmações recebidas no terminal do cliente e do servidor ✅
</details>

<details>
  <summary><strong>Entrega 2: Protocolo Sem Erros (21/10/2026)</strong></summary>

</details>

<details>
  <summary><strong>Entrega 3: Inserção de Erros e Perdas (23/11/2026)</strong></summary>

</details>

## Equipe

* André Borges Viana - abv2@cesar.school
* Eros Amancio Nascimento - ean@cesar.school
* Ian Felipe Costa van Drunen - ifcvd@cesar.school
* Lucas Coutinho de Almeida Bayma - lcab@cesar.school
* Luiz Felipe de Siqueira Gonçalves - lfgs@cesar.school
* Mateus Lins Farias - mlf2@cesar.school
* Pedro de Sá e Benevides de Lima Moreira - psblm@cesar.school
* Rafael Chiappetta Barboza - rcb2@cesar.school
* Telmo Melo Ferreira Calheiros - tmfc@cesar.school
* Thiago Neiva de Lima Santos - tnls@cesar.school