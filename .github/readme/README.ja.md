<h1 align="center">advice-debugger</h1>

<p align="center">
  <strong>あなたのAIはアドバイスをくれる。でも、それが効果があったかどうかは知らない。<br/>これからは、わかる。</strong>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/getcakedieyoungx/advice-debugger?style=flat" alt="ライセンス"></a>
  <a href="https://github.com/getcakedieyoungx/advice-debugger/actions/workflows/tests.yml"><img src="https://github.com/getcakedieyoungx/advice-debugger/actions/workflows/tests.yml/badge.svg" alt="テスト"></a>
  <img src="https://img.shields.io/badge/dependencies-0-brightgreen?style=flat" alt="依存関係ゼロ">
  <a href="https://www.patreon.com/monkeytax407"><img src="https://img.shields.io/badge/Patreon-support-F96854?style=flat&logo=patreon&logoColor=white" alt="Patreonで支援"></a>
</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <a href="README.tr.md" title="トルコ語">🇹🇷</a> ·
  <a href="README.es.md" title="スペイン語">🇪🇸</a> ·
  <a href="README.pt-BR.md" title="ポルトガル語（ブラジル）">🇧🇷</a> ·
  <a href="README.de.md" title="ドイツ語">🇩🇪</a> ·
  <a href="README.zh-CN.md" title="簡体字中国語">🇨🇳</a> ·
  <strong>🇯🇵</strong>
</p>

## インストール

これをClaude Code（または任意のコーディングエージェント）に貼り付けてください：

```text
Install the advice-debugger skill from https://github.com/getcakedieyoungx/advice-debugger, following the repo's AGENTS.md.
```

またはClaude Codeプラグインとして：

```bash
claude plugin marketplace add getcakedieyoungx/advice-debugger
claude plugin install advice-debugger@advice-debugger
```

その他のオプションは[INSTALL.md](../../INSTALL.md)にあります。

## 問題

コードにはテストがあります。修正が間違っていれば、何かが赤くなります。

アドバイスには何もありません。アシスタントが「毎日投稿して」とか「20人にコールドメールを送って」と言い、あなたが試しても、誰も予測できなかった理由で失敗する。そして翌週、同じアシスタントが同じアドバイスを別の言葉で繰り返す。結果を見ることは決してありません。

## 何が変わるのか

### 習慣

<table>
<tr>
<td width="50%">

**Before**

> **あなた:** 言われた通り毎日投稿してみた。3日やって、それでやめた。書くのは簡単だったけど、毎日何を書くか決めるのが疲れた。
>
> **AI:** 継続が鍵です！毎日リマインダーを設定して、アイデアリストを手元に置いて、小さな一歩の積み重ねを忘れないでください。短い投稿でもOKです。あなたならできます！💪

</td>
<td width="50%">

**After**

> **AI:** #1の結果を記録します。ボトルネックは*書くこと*だと仮定していました。実際は*毎日のトピック決定*でした。この仮定は崩れたので、リマインダーでは解決しません。
>
> **1週間試すこと:** 毎週日曜日に、5つのトピックを選び、40分のセッションで下書きを作成。平日は次の下書きを公開するだけ。
>
> **シグナル:** 7日間で5件以上の投稿。#2として記録（#1を改訂）、10月8日にチェックイン。

</td>
</tr>
</table>

### コードベース

<table>
<tr>
<td width="50%">

**Before**

> **あなた:** 2週間前に`shared/`を小さなパッケージに分割するよう言われました。今ではほとんどすべてのPRが4つのパッケージに触れています。
>
> **AI:** モジュラーアーキテクチャが落ち着くまでの間は正常です！Turborepoをキャッシュ用に追加し、ESLintで境界を強制し、あと数週間待ちましょう。きっと報われますよ。🚀

</td>
<td width="50%">

**After**

> **AI:** 推測ではなく、`git log`の直近14件のPRを#5と照合しました：
>
> ```diff
>   期待値     PRあたりのタッチパッケージ数 ≤ 2
> - 実際       PRあたり4、pricingとcheckoutが11/14で同時に変更
> ```
>
> **A1は破綻:** 「pricingとcheckoutは独立して変更される」。この2つを1つのパッケージに統合し、他の分割は維持してください。
>
> **シグナル:** 次の10件のPRでPRあたりのパッケージ数 ≤ 2。#6として記録（#5を改訂）。

</td>
</tr>
</table>

#5の台帳に記録される内容：

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

## 仕組み

実行可能なアドバイスはすべて、ローカルの台帳にある小さな反証可能な実験になります：

1. **仮定:** これが機能するために真でなければならないことは何か？1つは*クリティカル*とマークされます。
2. **期待される結果:** 何が変わるべきか、どの観察がそれを証明するか、いつまでに。
3. **小さな実験:** 1ヶ月の計画ではなく、クリティカルな仮定をテストする3〜14日間。
4. **比較:** 報告があったとき、各仮定は`held`、`broke`、`untested`のいずれかにマークされます。見落としていた仮定も書き留められます。
5. **次のアドバイス:** 破綻した仮定から始まり、古いエントリにリンクします。回答する前に、アシスタントはドラフトをすべての破綻した仮定と照合します。これにより、同じアドバイスが別の言葉で繰り返されるのを防ぎます。

台帳は新しいアドバイスを提供する**前に**チェックされるため、先月の実験からの教訓が今日の回答を形作ります。

チェックイン日が来ると、プラグインのセッション開始フックがアシスタントに、結果がどうだったかを1行で尋ねるよう促します。期限が来ていないときは沈黙を保ちます。

## 人格への判定はしない

1回の失敗した実験が「あなたには規律がない」になることはありません。教訓は**条件＋結果**として記録されます（「毎日新しい決断が必要なルーティンは3日目で停滞した」）。条件は再設計できますが、レッテルはできません。

## 役立つ場面

| 領域 | 学べること |
|---|---|
| 学習 | どの学習方法が実際に記憶を向上させるのか？ |
| ビジネス | どのアウトリーチチャネルが実際に返信を得られるのか？ |
| ソフトウェア | そのリファクタリングは本当にメンテナンスを減らしたのか？（git履歴が答える） |
| 計画 | 時間見積もりが一貫してずれるのはどこか？ |
| コンテンツ | 実際に持続可能な制作リズムはどれか？ |

## 台帳

`~/.advice-ledger/`にあるプレーンなJSONと、読みやすい`ledger.md`。Pythonスクリプト（標準ライブラリのみ）が、ロック、検証、バックアップ付きですべての書き込みを行います。[サンプル台帳](../../examples/example-ledger.md)を参照してください。

```text
$ python ledger.py lessons --domain content
#1 [content] abandoned: Post once every day
   x broke: The bottleneck is writing; picking topics is easy (the daily topic decision)
   -> lesson: A daily routine that needs a fresh decision every day stalled on day 3.
```

**プライバシー:** 台帳はローカルファイルであり、スクリプトはネットワーク呼び出しを行いません。アシスタントが読み取る部分は、開いた他のファイルと同様に、その会話の一部になります。場所は`ADVICE_LEDGER_DIR`で変更でき、リマインダーフックは`ADVICE_DEBUGGER_NO_HOOK=1`でオフにできます。

## カスタマイズ

フォークして、[`skills/advice-debugger/SKILL.md`](../../skills/advice-debugger/SKILL.md)を編集し、フォークをインストールします。テストは`python -m unittest discover -s tests`で実行します。

## サポート

advice-debuggerは無料でMITライセンスです。使い回しのアドバイスをもう一度受けるのを防いでくれたなら、[Patreon](https://www.patreon.com/monkeytax407)で同様のツールを支援できます。

## ライセンス

[MIT](../../LICENSE)。

あなたのアシスタントが同じ失敗したアドバイスを2回渡したことがあるなら、⭐を付けてください。
