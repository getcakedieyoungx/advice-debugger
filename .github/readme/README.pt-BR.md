<h1 align="center">advice-debugger</h1>

<p align="center">
  <strong>Sua IA te dá conselhos. Ela nunca descobre se funcionou.<br/>Agora descobre.</strong>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/getcakedieyoungx/advice-debugger?style=flat" alt="Licença"></a>
  <a href="https://github.com/getcakedieyoungx/advice-debugger/actions/workflows/tests.yml"><img src="https://github.com/getcakedieyoungx/advice-debugger/actions/workflows/tests.yml/badge.svg" alt="Testes"></a>
  <img src="https://img.shields.io/badge/dependencies-0-brightgreen?style=flat" alt="Zero dependências">
  <a href="https://www.patreon.com/monkeytax407"><img src="https://img.shields.io/badge/Patreon-support-F96854?style=flat&logo=patreon&logoColor=white" alt="Apoie no Patreon"></a>
</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <a href="README.tr.md" title="Türkçe">🇹🇷</a> ·
  <a href="README.es.md" title="Español">🇪🇸</a> ·
  <strong>🇧🇷</strong> ·
  <a href="README.de.md" title="Deutsch">🇩🇪</a> ·
  <a href="README.zh-CN.md" title="简体中文">🇨🇳</a> ·
  <a href="README.ja.md" title="日本語">🇯🇵</a>
</p>

## Instalação

Cole isto no Claude Code (ou em qualquer agente de codificação):

```text
Install the advice-debugger skill from https://github.com/getcakedieyoungx/advice-debugger, following the repo's AGENTS.md.
```

Ou como plugin do Claude Code:

```bash
claude plugin marketplace add getcakedieyoungx/advice-debugger
claude plugin install advice-debugger@advice-debugger
```

Mais opções em [INSTALL.md](../../INSTALL.md).

## O problema

Código tem testes. Quando uma correção está errada, algo fica vermelho.

Conselho não tem nada. Seu assistente te diz para "postar todo dia" ou "mandar e-mail frio para 20 pessoas", você tenta, falha por um motivo que ninguém previu, e na semana seguinte o mesmo assistente te dá o mesmo conselho com palavras diferentes. Ele nunca viu o resultado.

## O que muda

### Um hábito

<table>
<tr>
<td width="50%">

**Antes**

> **Você:** Tentei postar todo dia como você disse. Fiz 3 dias e desisti. Escrever era fácil, mas decidir sobre o que escrever todo santo dia me esgotou.
>
> **IA:** Consistência é a chave! Tente definir um lembrete diário, mantenha uma lista de ideias à mão e lembre-se de que pequenos passos se acumulam. Até um post curto conta. Você consegue! 💪

</td>
<td width="50%">

**Depois**

> **IA:** Registrando o resultado do #1. Assumimos que o gargalo era *escrever*. Descobriu-se que era a *decisão diária do tópico*. Essa suposição quebrou, então um lembrete não vai resolver.
>
> **Tente por uma semana:** todo domingo, escolha 5 tópicos e rascunhe-os em uma sessão de 40 minutos. Durante a semana, só publique o próximo rascunho.
>
> **Sinal:** ≥5 posts em 7 dias. Registrado como #2 (revisa o #1), check-in em 8 de outubro.

</td>
</tr>
</table>

### Uma base de código

<table>
<tr>
<td width="50%">

**Antes**

> **Você:** Há duas semanas você me disse para dividir `shared/` em pacotes pequenos. Agora quase todo PR mexe em quatro deles.
>
> **IA:** Isso é normal enquanto uma arquitetura modular se assenta! Adicione Turborepo para cache, imponha limites com ESLint e dê mais algumas semanas. Vai valer a pena. 🚀

</td>
<td width="50%">

**Depois**

> **IA:** Verifiquei o #5 contra os últimos 14 PRs no `git log` em vez de adivinhar:
>
> ```diff
>   esperado   ≤ 2 pacotes tocados por PR
> - real       4 por PR, pricing + checkout mudaram juntos em 11/14
> ```
>
> **A1 quebrou:** "pricing e checkout mudam de forma independente". Junte esses dois de volta em um único pacote e mantenha as outras divisões.
>
> **Sinal:** ≤ 2 pacotes por PR nos próximos 10 PRs. Registrado como #6 (revisa o #5).

</td>
</tr>
</table>

O que entra no registro para o #5:

```json
{
  "status": "failed",
  "actual": "Median PR touched 4 packages; pricing and checkout changed together in 11 of 14 PRs.",
  "gap": "expected <= 2 packages per PR, got 4",
  "verdicts": {
    "A1": { "verdict": "broke", "note": "pricing and checkout are one unit of change" },
    "A2": "held"
  },
  "lesson": "Splitting modules that change together multiplied the packages touched per PR.",
  "source": "git log, last 14 PRs"
}
```

## Como funciona

Cada conselho acionável vira um pequeno experimento falseável em um registro local:

1. **Suposições:** o que precisa ser verdade para isso funcionar? Uma é marcada como *crítica*.
2. **Resultado esperado:** o que deve mudar, qual observação prova isso e até quando.
3. **Experimento pequeno:** 3–14 dias que testam a suposição crítica, não um plano de um mês.
4. **Compare:** quando você reportar, cada suposição é marcada como `held`, `broke` ou `untested`. Suposições que passaram despercebidas também são anotadas.
5. **Próximo conselho:** parte da suposição que quebrou e faz referência à entrada antiga. Antes de responder, o assistente verifica seu rascunho contra toda suposição quebrada, o que deve impedir que o mesmo conselho volte com palavras novas.

O registro é verificado **antes** de dar um novo conselho, então a lição do experimento do mês passado molda a resposta de hoje.

Quando a data de check-in chega, o hook de início de sessão do plugin lembra o assistente de te perguntar, em uma linha, como foi. Ele fica em silêncio quando nada está pendente.

## Sem veredictos sobre caráter

Um experimento falho nunca vira "você não tem disciplina". Lições são registradas como **condição + resultado** ("uma rotina que precisava de uma decisão nova todo dia travou no dia 3"), porque condições podem ser redesenhadas e rótulos não.

## Onde ajuda

| Área | O que aprende |
|---|---|
| Aprendizado | Qual método de estudo realmente melhora a retenção? |
| Negócios | Qual canal de prospecção realmente gera respostas? |
| Software | Aquele refactor realmente reduziu a manutenção? (o histórico do git responde) |
| Planejamento | Onde suas estimativas de tempo erram consistentemente? |
| Conteúdo | Qual ritmo de produção você realmente consegue sustentar? |

## O registro

JSON simples em `~/.advice-ledger/`, além de um `ledger.md` legível. Um script Python (apenas biblioteca padrão) faz toda escrita com lock, validação e backup. Veja um [exemplo de registro](../../examples/example-ledger.md).

```text
$ python ledger.py lessons --domain content
#1 [content] abandoned: Post once every day
   x broke: The bottleneck is writing; picking topics is easy (the daily topic decision)
   -> lesson: A daily routine that needs a fresh decision every day stalled on day 3.
```

**Privacidade:** o registro é um arquivo local e o script não faz chamadas de rede. As partes que seu assistente lê fazem parte daquela conversa, como qualquer arquivo que ele abre. Mude o local com `ADVICE_LEDGER_DIR` e desligue o hook de lembrete com `ADVICE_DEBUGGER_NO_HOOK=1`.

## Ajuste

Faça um fork, edite [`skills/advice-debugger/SKILL.md`](../../skills/advice-debugger/SKILL.md) e instale seu fork. Rode os testes com `python -m unittest discover -s tests`.

## Apoie

advice-debugger é gratuito e licenciado sob MIT. Se ele te salvou de mais uma rodada de conselhos reciclados, você pode apoiar mais ferramentas como esta no [Patreon](https://www.patreon.com/monkeytax407).

## Licença

[MIT](../../LICENSE).

Dê uma estrela ⭐ se seu assistente já te entregou o mesmo conselho falho duas vezes.
