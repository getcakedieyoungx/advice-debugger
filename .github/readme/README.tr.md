<h1 align="center">advice-debugger</h1>

<p align="center">
  <strong>Yapay zekâ sana tavsiye veriyor. İşe yarayıp yaramadığını hiç öğrenmiyor.<br/>Artık öğreniyor.</strong>
</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> · <strong>🇹🇷</strong>
</p>

## Kurulum

Claude Code'a (ya da herhangi bir kodlama ajanına) yapıştır:

```text
Install the advice-debugger skill from https://github.com/getcakedieyoungx/advice-debugger, following the repo's AGENTS.md.
```

Ya da Claude Code eklentisi olarak:

```bash
claude plugin marketplace add getcakedieyoungx/advice-debugger
claude plugin install advice-debugger@advice-debugger
```

Diğer yollar: [INSTALL.md](../../INSTALL.md).

## Sorun

Kodda test var: çözüm yanlışsa bir şey kırmızı yanar.

Tavsiyede hiçbir şey yok. Asistan "her gün paylaşım yap" ya da "20 kişiye soğuk mail at" der. Sen denersin, kimsenin öngörmediği bir nedenle olmaz. Bir hafta sonra aynı asistan aynı tavsiyeyi başka kelimelerle yeniden verir, çünkü sonucu hiç görmedi.

## Ne değişiyor

<table>
<tr>
<td width="50%">

### Önce

> **Sen:** Dediğin gibi her gün paylaşım yapmayı denedim. 3 gün gitti, bıraktım. Yazmak kolaydı ama her gün ne yazacağıma karar vermek beni yordu.
>
> **AI:** Süreklilik çok önemli! Günlük bir hatırlatıcı kur, fikir listesi tut. Küçük adımlar birikir, kısa bir paylaşım bile sayılır. Yaparsın! 💪

</td>
<td width="50%">

### Sonra

> **AI:** #1'in sonucunu kaydediyorum. Darboğazın *yazmak* olduğunu varsaymıştık, *her gün konu seçmek* çıktı. O varsayım çöktü, yani hatırlatıcı bunu çözmez.
>
> **Bir hafta dene:** her pazar 40 dakikalık tek oturumda 5 konu seç ve taslaklarını yaz. Hafta içi yalnız sıradaki taslağı yayınla.
>
> **Sinyal:** 7 günde ≥5 paylaşım. #2 olarak kaydettim (#1'i düzeltiyor), 8 Ekim'de bakarız.

</td>
</tr>
</table>

## Nasıl çalışıyor

Uygulanabilir her tavsiye, yerel bir defterde küçük ve yanlışlanabilir bir deneye dönüşür:

1. **Varsayımlar:** bunun işe yaraması için ne doğru olmalı? Biri *kritik* olarak işaretlenir.
2. **Beklenen sonuç:** ne değişmeli, hangi gözlem bunu gösterir, ne zamana kadar.
3. **Küçük deneme:** bir aylık plan yerine kritik varsayımı sınayan 3–14 gün.
4. **Karşılaştırma:** sonucu anlattığında her varsayım `held` (tuttu), `broke` (çöktü) ya da `untested` (sınanmadı) diye işaretlenir. Gözden kaçmış varsayımlar da yazılır.
5. **Sonraki tavsiye:** çöken varsayımdan başlar ve eski kayda bağlanır. Asistan cevap vermeden önce taslağını her çöken varsayımla karşılaştırır. Bu adım, aynı tavsiyenin başka kelimelerle geri gelmesini engellemek için var.

Defter yeni tavsiyeden **önce** okunur, böylece geçen ayki denemenin dersi bugünkü cevabı şekillendirir. Bir kontrol tarihi geldiğinde eklentinin oturum başı hook'u asistana sonucu tek satırla sormasını hatırlatır. Kontrol günü gelmiş deneme yoksa sessiz kalır.

## Kişilik yargısı yok

Tek bir başarısız deneme asla "disiplinin yok" sonucuna dönüşmez. Dersler **koşul + sonuç** olarak kaydedilir ("her gün yeni bir karar gerektiren rutin 3. günde durdu"). Koşul yeniden tasarlanabilir, etiket tasarlanamaz.

## Gizlilik

Defter (`~/.advice-ledger/`) yerel bir dosyadır ve script hiçbir ağ çağrısı yapmaz. Asistanın okuduğu kısım, açtığı her dosya gibi o konuşmanın parçası olur. Konumu `ADVICE_LEDGER_DIR` ile değiştirebilirsin; hatırlatıcıyı `ADVICE_DEBUGGER_NO_HOOK=1` ile kapatırsın.

## Lisans

[MIT](../../LICENSE).

Asistanın sana aynı başarısız tavsiyeyi iki kez verdiyse ⭐ bırak.
