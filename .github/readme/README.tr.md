<h1 align="center">advice-debugger</h1>

<p align="center">
  <strong>Yapay zekân sana tavsiye verir. Ama işe yarayıp yaramadığını asla öğrenmez.<br/>Artık öğrenecek.</strong>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/getcakedieyoungx/advice-debugger?style=flat" alt="Lisans"></a>
  <a href="https://github.com/getcakedieyoungx/advice-debugger/actions/workflows/tests.yml"><img src="https://github.com/getcakedieyoungx/advice-debugger/actions/workflows/tests.yml/badge.svg" alt="Testler"></a>
  <img src="https://img.shields.io/badge/dependencies-0-brightgreen?style=flat" alt="Sıfır bağımlılık">
  <a href="https://www.patreon.com/monkeytax407"><img src="https://img.shields.io/badge/Patreon-support-F96854?style=flat&logo=patreon&logoColor=white" alt="Patreon'da destekle"></a>
</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <strong>🇹🇷</strong> ·
  <a href="README.es.md" title="İspanyolca">🇪🇸</a> ·
  <a href="README.pt-BR.md" title="Portekizce (Brezilya)">🇧🇷</a> ·
  <a href="README.de.md" title="Almanca">🇩🇪</a> ·
  <a href="README.zh-CN.md" title="Basitleştirilmiş Çince">🇨🇳</a> ·
  <a href="README.ja.md" title="Japonca">🇯🇵</a>
</p>

## Kurulum

Bunu Claude Code'a (veya herhangi bir kodlama ajanına) yapıştır:

```text
Install the advice-debugger skill from https://github.com/getcakedieyoungx/advice-debugger, following the repo's AGENTS.md.
```

Ya da Claude Code eklentisi olarak:

```bash
claude plugin marketplace add getcakedieyoungx/advice-debugger
claude plugin install advice-debugger@advice-debugger
```

Daha fazla seçenek için [INSTALL.md](../../INSTALL.md).

## Sorun

Kodda test var: düzeltme yanlışsa bir şey kırmızı yanar.

Tavsiyede hiçbir şey yok. Asistan "her gün paylaşım yap" ya da "20 kişiye soğuk mail at" der. Sen denersin, kimsenin öngörmediği bir nedenle olmaz. Bir hafta sonra aynı asistan aynı tavsiyeyi başka kelimelerle yeniden verir, çünkü sonucu hiç görmedi.

## Ne değişiyor

### Bir alışkanlık

<table>
<tr>
<td width="50%">

**Öncesi**

> **Sen:** Dediğin gibi her gün paylaşmayı denedim. 3 gün yaptım, sonra bıraktım. Yazmak kolaydı ama her gün ne hakkında yazacağıma karar vermek beni yordu.
>
> **AI:** Süreklilik çok önemli! Günlük bir hatırlatıcı kur, bir fikir listesi tut ve küçük adımların biriktiğini unutma. Kısa bir paylaşım bile sayılır. Başaracaksın! 💪

</td>
<td width="50%">

**Sonrası**

> **AI:** #1'in sonucunu kaydediyorum. Darboğazın *yazmak* olduğunu varsaymıştık. Meğer *her gün konu seçmek*miş. Bu varsayım çöktü, yani hatırlatıcı bunu düzeltmez.
>
> **Bir hafta dene:** her Pazar, 5 konu seç ve 40 dakikalık tek oturumda taslaklarını çıkar. Hafta içi sadece sıradaki taslağı yayınla.
>
> **Sinyal:** 7 günde ≥5 paylaşım. #2 olarak kaydettim (#1'i düzeltiyor), 8 Ekim'de bakarız.

</td>
</tr>
</table>

### Bir kod tabanı

<table>
<tr>
<td width="50%">

**Öncesi**

> **Sen:** İki hafta önce `shared/` klasörünü küçük paketlere bölmemi söylemiştin. Şimdi neredeyse her PR dört tanesine dokunuyor.
>
> **AI:** Modüler mimari otururken bu normal! Turborepo ile önbellekleme ekle, ESLint ile sınırları zorunlu kıl ve birkaç hafta daha ver. Karşılığını alacaksın. 🚀

</td>
<td width="50%">

**Sonrası**

> **AI:** Tahmin etmek yerine #5'i `git log`'daki son 14 PR ile kontrol ettim:
>
> ```diff
>   beklenen   PR başına ≤ 2 pakete dokunulması
> - gerçek     PR başına 4, fiyatlandırma + ödeme 14 PR'ın 11'inde birlikte değişti
> ```
>
> **A1 çöktü:** "fiyatlandırma ve ödeme bağımsız değişir". Bu ikisini tek pakette birleştir, diğer bölmeleri koru.
>
> **Sinyal:** Sonraki 10 PR'da PR başına ≤ 2 paket. #6 olarak kaydettim (#5'i düzeltiyor).

</td>
</tr>
</table>

#5 için deftere düşen kayıt:

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

## Nasıl çalışır

Her uygulanabilir tavsiye, yerel kayıt defterinde küçük, çürütülebilir bir deneye dönüşür:

1. **Varsayımlar:** Bunun işe yaraması için ne doğru olmalı? Biri *kritik* olarak işaretlenir.
2. **Beklenen sonuç:** Ne değişmeli, hangi gözlem bunu kanıtlar ve ne zamana kadar.
3. **Küçük deney:** Bir aylık plan değil, kritik varsayımı test eden 3–14 gün.
4. **Karşılaştır:** Geri bildirim verdiğinde her varsayım `held`, `broke` veya `untested` olarak işaretlenir. Gözden kaçmış varsayımlar da yazılır.
5. **Sonraki tavsiye:** Çöken varsayımdan başlar ve eski kayda bağlanır. Asistan cevap vermeden önce taslağını her çöken varsayıma karşı kontrol eder; bu, aynı tavsiyenin yeni kelimelerle geri gelmesini engellemek içindir.

Kayıt defteri yeni tavsiye verilmeden **önce** kontrol edilir, böylece geçen ayki deneyin dersi bugünün cevabını şekillendirir.

Kontrol tarihi geldiğinde, eklentinin oturum başı hook'u asistana tek satırda nasıl gittiğini sormasını hatırlatır. Kontrol günü gelmiş deneme yoksa sessiz kalır.

## Kişilik yargıları yok

Başarısız bir deney asla "disiplinin yok" sonucuna dönüşmez. Dersler **durum + sonuç** olarak kaydedilir ("her gün yeni bir karar gerektiren bir rutin 3. günde durdu"), çünkü durumlar yeniden tasarlanabilir, etiketler tasarlanamaz.

## Nerede işe yarar

| Alan | Ne öğrenir |
|---|---|
| Öğrenme | Hangi çalışma yöntemi gerçekten hatırlamayı geliştiriyor? |
| İş | Hangi müşteri bulma kanalı gerçekten yanıt getiriyor? |
| Yazılım | Bu refactor bakımı gerçekten azalttı mı? (git geçmişi cevaplar) |
| Planlama | Zaman tahminlerin sürekli nerede tutmuyor? |
| İçerik | Hangi üretim ritmini gerçekten sürdürebiliyorsun? |

## Kayıt defteri

`~/.advice-ledger/` içinde düz JSON, ayrıca okunabilir bir `ledger.md`. Bir Python betiği (yalnızca standart kütüphane) her yazmayı kilit, doğrulama ve yedekleme ile yapar. Bir [örnek deftere](../../examples/example-ledger.md) bak.

```text
$ python ledger.py lessons --domain content
#1 [content] abandoned: Post once every day
   x broke: The bottleneck is writing; picking topics is easy (the daily topic decision)
   -> lesson: A daily routine that needs a fresh decision every day stalled on day 3.
```

**Gizlilik:** kayıt defteri yerel bir dosyadır ve betik hiçbir ağ çağrısı yapmaz. Asistanının okuduğu kısımlar, açtığı herhangi bir dosya gibi, o konuşmanın parçası olur. Konumu `ADVICE_LEDGER_DIR` ile değiştir ve hatırlatma hook'unu `ADVICE_DEBUGGER_NO_HOOK=1` ile kapat.

## Özelleştir

Fork'la, [`skills/advice-debugger/SKILL.md`](../../skills/advice-debugger/SKILL.md) dosyasını düzenle ve kendi fork'unu kur. Testleri `python -m unittest discover -s tests` ile çalıştır.

## Destek

advice-debugger ücretsiz ve MIT lisanslıdır. Seni aynı tavsiyeyi bir tur daha dinlemekten kurtardıysa, [Patreon](https://www.patreon.com/monkeytax407) üzerinden buna benzer daha fazla aracı destekleyebilirsin.

## Lisans

[MIT](../../LICENSE).

Asistanın sana aynı başarısız tavsiyeyi iki kez verdiyse ⭐ bırak.
