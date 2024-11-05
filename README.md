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

#### 特殊攻撃（消費コンボ数）

- ５つのビームを同時に放つ：`Z`を押しながら`SPACE`（0）
- 一定時間、重力場を出して敵を消滅させる：`BACK`（20）
- 一定時間、敵機を行動不能にし、爆弾を鈍化させる：`E`（20）
- 一定時間、攻撃を防ぐシールドを１つだけ装備する：`A`（10）

### ルール詳細

- 敵や敵からの攻撃を倒すごとにスコアが加算される
- 連続で倒すことでスコアとは別に「コンボ」が加算される
- コンボを消費することで特殊攻撃を使用できる
- ステージ内にときどき現れるコインでもコンボを獲得できる（1 枚で+10 コンボ）

## ゲームの実装

### 共通基本機能

- 背景画像と主人公キャラクターの描画
- 操作に応じてビームを描画

### 担当追加機能

<必ず実装する機能>

- 時間表示(カウントアップ)（担当：安田）
- ステージをランダムで変える（担当：平塚）
- 残機と HP の追加（担当：稲玉）
- UFO の上下、左右運動（担当：稲玉）
- ちいさな爆発エフェクト（担当：稲玉）
- ボーナスコインの出現（担当：田中）
- コンボ制の導入（担当：菊池）

<余裕があったら実装する機能>

- 操作方法の表示
- ビームの変更（担当：平塚）
- ボスキャラの登場（担当：菊池）

### ToDo

- [x] time モジュールを利用して上部に経過時間を表示
- [x] 背景画像を複数用意、ランダムに選択して描画
- [x] こうかとんの体力に関する機能追加
- [x] 新たに Coin クラスを作成；ランダムな位置にボーナスコインを描画する
- [x] 新たに Combo クラスを作成；敵を連続で倒したりコインを獲得したりするとコンボが増える
- [ ] 操作方法をまとめた画像を作り、ゲーム開始時に表示
- [ ] ビームをぽよぽよしている感じに変更
- [ ] 新たに Boss クラスを作成；経過時間によって周囲の敵を消去し、ボスを描画する

### メモ

- すべてのクラスに関係する関数は，クラスの外で定義してある
- 各クラスをクラス群に分類して整理している
- Python の基本的なコード規約は厳守すること
