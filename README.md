# こうかとん ⭐ お空のぽよぽよシューティング ⭐

## 実行環境の必要条件

- python >= 3.10
- pygame >= 2.1

## ゲームの概要

主人公キャラクターこうかとんをキーボードで操作するシューティングゲーム。

連続で敵を倒すとコンボボーナスを獲得！コンボを貯めて必殺技を繰り出そう！

一定時間が経過すると現れるボスを倒せばゲームクリアとなる。

## ゲームの遊び方

### 操作

- 移動 `W` `A` `S` `D`
- 攻撃 `SPACE`
-

### ルール詳細

- 敵や敵からの攻撃を倒すごとにスコアが加算される
- 連続で倒すことでスコアとは別に「コンボ」が加算される
- コンボを消費することで特殊攻撃を使用できる
- ステージ内にときどき現れるコインでもコンボを獲得できる
-

## ゲームの実装

### 共通基本機能

- 背景画像と主人公キャラクターの描画
- 操作に応じてビームを描画

### 担当追加機能

- 時間表示(カウントアップ)（担当：安田）
- ステージをランダムで変える（担当：平塚）
- 残機と HP の追加（担当：稲玉）
- ボスキャラの登場（担当：）
- ボーナスコインの出現（担当：田中）
- コンボ制の導入（担当：菊池）
- 操作方法の表示（担当：）
- ビームの変更（担当：平塚）

### ToDo

- [ ] time モジュールを利用して上部中央に経過時間を表示
- [ ] 背景画像を複数用意、ランダムに選択して描画
- [ ] Bird クラスへの変更；体力に関する機能追加
- [ ] main 関数の冒頭を編集；適宜操作方法を変える
- [ ] 新たに Boss クラスを作成；経過時間によって周囲の敵を消去し、ボスを描画する
- [ ] 新たに Coin クラスを作成；ランダムな位置にボーナスコインを描画する
- [ ] 新たに Combo クラスを作成；敵を連続で倒したりコインを獲得したりするとコンボが増える
- [ ] 操作方法をまとめた画像を作り、ゲーム開始時に表示
- [ ] ビームをぽよぽよしている感じに変更

### メモ

- すべてのクラスに関係する関数は，クラスの外で定義してある
- 各クラスをクラス群に分類して整理している
- Python の基本的なコード規約は厳守すること
