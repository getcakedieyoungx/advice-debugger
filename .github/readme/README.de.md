<h1 align="center">advice-debugger</h1>

<p align="center">
  <strong>Deine KI gibt dir Ratschläge. Sie erfährt nie, ob sie funktioniert haben.<br/>Jetzt schon.</strong>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/getcakedieyoungx/advice-debugger?style=flat" alt="Lizenz"></a>
  <a href="https://github.com/getcakedieyoungx/advice-debugger/actions/workflows/tests.yml"><img src="https://github.com/getcakedieyoungx/advice-debugger/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
  <img src="https://img.shields.io/badge/dependencies-0-brightgreen?style=flat" alt="Keine Abhängigkeiten">
  <a href="https://www.patreon.com/monkeytax407"><img src="https://img.shields.io/badge/Patreon-support-F96854?style=flat&logo=patreon&logoColor=white" alt="Unterstütze auf Patreon"></a>
</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <a href="README.tr.md" title="Türkçe">🇹🇷</a> ·
  <a href="README.es.md" title="Español">🇪🇸</a> ·
  <a href="README.pt-BR.md" title="Português (Brasil)">🇧🇷</a> ·
  <strong>🇩🇪</strong> ·
  <a href="README.zh-CN.md" title="简体中文">🇨🇳</a> ·
  <a href="README.ja.md" title="日本語">🇯🇵</a>
</p>

## Installation

Füge das hier in Claude Code (oder einen anderen Coding-Agenten) ein:

```text
Install the advice-debugger skill from https://github.com/getcakedieyoungx/advice-debugger, following the repo's AGENTS.md.
```

Oder als Claude-Code-Plugin:

```bash
claude plugin marketplace add getcakedieyoungx/advice-debugger
claude plugin install advice-debugger@advice-debugger
```

Weitere Optionen in [INSTALL.md](../../INSTALL.md).

## Das Problem

Code hat Tests. Wenn ein Fix falsch ist, wird etwas rot.

Ratschläge haben nichts. Dein Assistent sagt dir „poste jeden Tag" oder „schreib 20 Leuten eine Kaltakquise-Mail", du probierst es, es scheitert aus einem Grund, den niemand vorhergesehen hat, und nächste Woche gibt dir derselbe Assistent denselben Rat in anderen Worten. Er hat das Ergebnis nie gesehen.

## Was sich ändert

### Eine Gewohnheit

<table>
<tr>
<td width="50%">

**Vorher**

> **Du:** Ich habe versucht, jeden Tag zu posten, wie du gesagt hast. Habe 3 Tage durchgehalten, dann aufgehört. Schreiben war einfach, aber mich jeden Tag zu entscheiden, worüber ich schreibe, hat mich ausgelaugt.
>
> **KI:** Konsistenz ist der Schlüssel! Versuch eine tägliche Erinnerung einzurichten, halte eine Ideenliste bereit und denk daran, dass kleine Schritte sich summieren. Auch ein kurzer Post zählt. Du schaffst das! 💪

</td>
<td width="50%">

**Nachher**

> **KI:** Protokolliere das Ergebnis von #1. Wir haben angenommen, der Engpass sei das *Schreiben*. Es stellte sich heraus, dass es die *tägliche Themenentscheidung* war. Diese Annahme hat sich als falsch erwiesen, also wird eine Erinnerung das nicht beheben.
>
> **Versuch es eine Woche lang:** wähle jeden Sonntag 5 Themen und entwirf sie in einer 40-minütigen Session. Unter der Woche veröffentlichst du nur noch den nächsten Entwurf.
>
> **Signal:** ≥5 Posts in 7 Tagen. Protokolliert als #2 (überarbeitet #1), Check-in am 8. Okt.

</td>
</tr>
</table>

### Eine Codebasis

<table>
<tr>
<td width="50%">

**Vorher**

> **Du:** Vor zwei Wochen hast du mir gesagt, ich soll `shared/` in kleine Pakete aufteilen. Jetzt betrifft fast jeder PR vier davon.
>
> **KI:** Das ist normal, während sich eine modulare Architektur setzt! Füge Turborepo für Caching hinzu, erzwinge Grenzen mit ESLint und gib es noch ein paar Wochen. Es wird sich auszahlen. 🚀

</td>
<td width="50%">

**Nachher**

> **KI:** Habe #5 gegen die letzten 14 PRs in `git log` geprüft, statt zu raten:
>
> ```diff
>   erwartet    ≤ 2 Pakete pro PR betroffen
> - tatsächlich 4 pro PR, pricing + checkout änderten sich zusammen in 11/14
> ```
>
> **A1 ist zerbrochen:** „pricing und checkout ändern sich unabhängig". Füge diese beiden wieder zu einem Paket zusammen und behalte die anderen Aufteilungen.
>
> **Signal:** ≤ 2 Pakete pro PR über die nächsten 10 PRs. Protokolliert als #6 (überarbeitet #5).

</td>
</tr>
</table>

Was für #5 im Ledger landet:

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

## So funktioniert's

Jeder umsetzbare Ratschlag wird zu einem kleinen, widerlegbaren Experiment in einem lokalen Ledger:

1. **Annahmen:** Was muss wahr sein, damit das funktioniert? Eine wird als *kritisch* markiert.
2. **Erwartetes Ergebnis:** Was sollte sich ändern, welche Beobachtung beweist es und bis wann.
3. **Kleines Experiment:** 3–14 Tage, die die kritische Annahme testen, kein Monatsplan.
4. **Vergleich:** Wenn du berichtest, wird jede Annahme als `held`, `broke` oder `untested` markiert. Übersehene Annahmen werden ebenfalls notiert.
5. **Nächster Ratschlag:** startet von der zerbrochenen Annahme und verlinkt auf den alten Eintrag. Bevor der Assistent antwortet, prüft er seinen Entwurf gegen jede zerbrochene Annahme – das soll verhindern, dass derselbe Rat in neuen Worten wiederkommt.

Das Ledger wird **vor** neuem Rat geprüft, damit die Lektion aus dem Experiment vom letzten Monat die heutige Antwort prägt.

Wenn ein Check-in-Datum erreicht ist, erinnert der Session-Start-Hook des Plugins den Assistenten, dich in einer Zeile zu fragen, wie es gelaufen ist. Er schweigt, wenn nichts fällig ist.

## Keine Charakterurteile

Ein fehlgeschlagenes Experiment wird nie zu „dir fehlt Disziplin". Lektionen werden als **Bedingung + Ergebnis** festgehalten („eine Routine, die täglich eine neue Entscheidung brauchte, scheiterte an Tag 3"), weil Bedingungen neu gestaltet werden können und Etiketten nicht.

## Wo es hilft

| Bereich | Was es lernt |
|---|---|
| Lernen | Welche Lernmethode verbessert tatsächlich das Erinnern? |
| Business | Welcher Outreach-Kanal bringt tatsächlich Antworten? |
| Software | Hat das Refactoring den Wartungsaufwand wirklich reduziert? (git history beantwortet das) |
| Planung | Wo sind deine Zeitschätzungen durchgehend daneben? |
| Content | Welchen Produktionsrhythmus kannst du tatsächlich durchhalten? |

## Das Ledger

Einfaches JSON in `~/.advice-ledger/`, plus ein lesbares `ledger.md`. Ein Python-Skript (nur Standardbibliothek) macht jeden Schreibvorgang mit Lock, Validierung und Backup. Siehe ein [Beispiel-Ledger](../../examples/example-ledger.md).

```text
$ python ledger.py lessons --domain content
#1 [content] abandoned: Post once every day
   x broke: The bottleneck is writing; picking topics is easy (the daily topic decision)
   -> lesson: A daily routine that needs a fresh decision every day stalled on day 3.
```

**Datenschutz:** Das Ledger ist eine lokale Datei und das Skript macht keine Netzwerkaufrufe. Die Teile, die dein Assistent liest, werden Teil dieses Gesprächs, wie jede andere Datei, die er öffnet. Ändere den Speicherort mit `ADVICE_LEDGER_DIR` und schalte den Erinnerungs-Hook mit `ADVICE_DEBUGGER_NO_HOOK=1` ab.

## Anpassen

Forke es, bearbeite [`skills/advice-debugger/SKILL.md`](../../skills/advice-debugger/SKILL.md) und installiere deinen Fork. Führe die Tests mit `python -m unittest discover -s tests` aus.

## Unterstützung

advice-debugger ist kostenlos und MIT-lizenziert. Wenn es dich vor einer weiteren Runde recycelter Ratschläge bewahrt hat, kannst du weitere solche Tools auf [Patreon](https://www.patreon.com/monkeytax407) unterstützen.

## Lizenz

[MIT](../../LICENSE).

Gib einen Stern ⭐, wenn dein Assistent dir schon einmal denselben fehlgeschlagenen Rat zweimal gegeben hat.
