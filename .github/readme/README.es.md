<h1 align="center">advice-debugger</h1>

<p align="center">
  <strong>Tu IA te da consejos. Nunca se entera de si funcionaron.<br/>Ahora sí.</strong>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/getcakedieyoungx/advice-debugger?style=flat" alt="Licencia"></a>
  <a href="https://github.com/getcakedieyoungx/advice-debugger/actions/workflows/tests.yml"><img src="https://github.com/getcakedieyoungx/advice-debugger/actions/workflows/tests.yml/badge.svg" alt="Pruebas"></a>
  <img src="https://img.shields.io/badge/dependencies-0-brightgreen?style=flat" alt="Cero dependencias">
  <a href="https://www.patreon.com/monkeytax407"><img src="https://img.shields.io/badge/Patreon-support-F96854?style=flat&logo=patreon&logoColor=white" alt="Apóyanos en Patreon"></a>
</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <a href="README.tr.md" title="Türkçe">🇹🇷</a> ·
  <strong>🇪🇸</strong> ·
  <a href="README.pt-BR.md" title="Português (Brasil)">🇧🇷</a> ·
  <a href="README.de.md" title="Deutsch">🇩🇪</a> ·
  <a href="README.zh-CN.md" title="简体中文">🇨🇳</a> ·
  <a href="README.ja.md" title="日本語">🇯🇵</a>
</p>

## Instalación

Pega esto en Claude Code (o cualquier agente de código):

```text
Install the advice-debugger skill from https://github.com/getcakedieyoungx/advice-debugger, following the repo's AGENTS.md.
```

O como plugin de Claude Code:

```bash
claude plugin marketplace add getcakedieyoungx/advice-debugger
claude plugin install advice-debugger@advice-debugger
```

Más opciones en [INSTALL.md](../../INSTALL.md).

## El problema

El código tiene pruebas. Cuando una corrección falla, algo se pone en rojo.

Los consejos no tienen nada. Tu asistente te dice "publica todos los días" o "envía correos en frío a 20 personas", lo intentas, falla por una razón que nadie predijo, y la semana siguiente el mismo asistente te da el mismo consejo con otras palabras. Nunca vio el resultado.

## Qué cambia

### Un hábito

<table>
<tr>
<td width="50%">

**Antes**

> **Tú:** Intenté publicar todos los días como dijiste. Aguanté 3 días y lo dejé. Escribir era fácil, pero decidir sobre qué escribir cada día me agotó.
>
> **IA:** ¡La constancia es clave! Prueba poner un recordatorio diario, ten una lista de ideas a mano, y recuerda que los pequeños pasos suman. Hasta una publicación corta cuenta. ¡Tú puedes! 💪

</td>
<td width="50%">

**Después**

> **IA:** Registrando el resultado de #1. Asumimos que el cuello de botella era *escribir*. Resultó ser la *decisión diaria del tema*. Esa suposición se rompió, así que un recordatorio no lo va a arreglar.
>
> **Prueba por una semana:** cada domingo, elige 5 temas y redáctalos en una sesión de 40 minutos. Entre semana, solo publica el siguiente borrador.
>
> **Señal:** ≥5 publicaciones en 7 días. Registrado como #2 (revisa #1), seguimiento el 8 de octubre.

</td>
</tr>
</table>

### Una base de código

<table>
<tr>
<td width="50%">

**Antes**

> **Tú:** Hace dos semanas me dijiste que dividiera `shared/` en paquetes pequeños. Ahora casi todos los PR tocan cuatro de ellos.
>
> **IA:** ¡Es normal mientras una arquitectura modular se asienta! Agrega Turborepo para caché, impón límites con ESLint, y dale unas semanas más. Va a dar frutos. 🚀

</td>
<td width="50%">

**Después**

> **IA:** Verifiqué #5 contra los últimos 14 PR en `git log` en lugar de adivinar:
>
> ```diff
>   esperado     ≤ 2 paquetes tocados por PR
> - real         4 por PR, pricing y checkout cambiaron juntos en 11/14
> ```
>
> **A1 se rompió:** "pricing y checkout cambian de forma independiente". Fusiona esos dos de nuevo en un solo paquete y mantén las otras divisiones.
>
> **Señal:** ≤ 2 paquetes por PR en los próximos 10 PR. Registrado como #6 (revisa #5).

</td>
</tr>
</table>

Lo que queda registrado para #5:

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

## Cómo funciona

Cada consejo accionable se convierte en un pequeño experimento falsable en un registro local:

1. **Suposiciones:** ¿qué tiene que ser cierto para que esto funcione? Una se marca como *crítica*.
2. **Resultado esperado:** qué debería cambiar, qué observación lo demuestra, y para cuándo.
3. **Experimento pequeño:** 3–14 días que prueban la suposición crítica, no un plan de un mes.
4. **Comparar:** cuando reportas, cada suposición se marca como `held`, `broke` o `untested`. Las suposiciones que se pasaron por alto también se anotan.
5. **Siguiente consejo:** parte de la suposición que se rompió y enlaza con la entrada anterior. Antes de responder, el asistente revisa su borrador contra cada suposición rota, para evitar que el mismo consejo vuelva con otras palabras.

El registro se revisa **antes** de dar un consejo nuevo, así la lección del experimento del mes pasado moldea la respuesta de hoy.

Cuando llega la fecha de seguimiento, el hook de inicio de sesión del plugin le recuerda al asistente preguntarte, en una línea, cómo fue. Se queda callado cuando no hay nada pendiente.

## Sin veredictos sobre la persona

Un experimento fallido nunca se convierte en "te falta disciplina". Las lecciones se registran como **condición + resultado** ("una rutina que necesitaba una decisión nueva cada día se estancó el día 3"), porque las condiciones se pueden rediseñar y las etiquetas no.

## Dónde ayuda

| Área | Qué aprende |
|---|---|
| Aprendizaje | ¿Qué método de estudio realmente mejora la retención? |
| Negocios | ¿Qué canal de divulgación realmente genera respuestas? |
| Software | ¿Ese refactor realmente redujo el mantenimiento? (el historial de git lo responde) |
| Planificación | ¿Dónde fallan consistentemente tus estimaciones de tiempo? |
| Contenido | ¿Qué ritmo de producción puedes sostener de verdad? |

## El registro

JSON plano en `~/.advice-ledger/`, más un `ledger.md` legible. Un script de Python (solo biblioteca estándar) hace cada escritura con bloqueo, validación y respaldo. Mira un [ejemplo de registro](../../examples/example-ledger.md).

```text
$ python ledger.py lessons --domain content
#1 [content] abandoned: Post once every day
   x broke: The bottleneck is writing; picking topics is easy (the daily topic decision)
   -> lesson: A daily routine that needs a fresh decision every day stalled on day 3.
```

**Privacidad:** el registro es un archivo local y el script no hace llamadas de red. Las partes que tu asistente lee se vuelven parte de esa conversación, como cualquier archivo que abra. Cambia la ubicación con `ADVICE_LEDGER_DIR`, y desactiva el hook de recordatorio con `ADVICE_DEBUGGER_NO_HOOK=1`.

## Personalízalo

Haz un fork, edita [`skills/advice-debugger/SKILL.md`](../../skills/advice-debugger/SKILL.md), e instala tu fork. Ejecuta las pruebas con `python -m unittest discover -s tests`.

## Apoyo

advice-debugger es gratuito y tiene licencia MIT. Si te salvó de otra ronda de consejos reciclados, puedes apoyar más herramientas como esta en [Patreon](https://www.patreon.com/monkeytax407).

## Licencia

[MIT](../../LICENSE).

Dale una estrella ⭐ si tu asistente alguna vez te dio el mismo consejo fallido dos veces.
