# シフト自動生成システム
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

遺伝的アルゴリズムを使用してシフトスケジュールを自動生成するシステムです。


## 🚀 クイックスタート

### 1. リポジトリのクローン
```bash
git clone https://github.com/iuti/shift-scheduler-ga.git
cd shift-scheduler-ga
```

### 2. 環境構築
```bash
# 仮想環境の作成
python -m venv .venv

# 仮想環境の有効化
# Windows
.venv\Scripts\activate
# macOS/Linux  
source .venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 3. 実行
```bash
python main.py
```

## 📊 デモ

実行すると以下のような出力が得られます：

```
シフト自動生成システムを開始します...
希望シフトファイルを読み込み中: data/hope_data.txt
読み込み完了: 26人のスタッフ
相性ペアファイルを読み込み中: data/negative.txt
相性の悪いペア: 12組

遺伝的アルゴリズムを実行中...
世代 0: 最大適応度 = -15420.00, 平均適応度 = -18250.50
世代 10: 最大適応度 = -12800.00, 平均適応度 = -15200.30
...
```

## 📁 プロジェクト構造

```
shiftGA/
├── main.py              # メインアプリケーション
├── config.py            # 設定パラメータ
├── data_loader.py       # データ読み込み処理
├── evaluator.py         # 適応度評価とスケジュール制約チェック
├── optimizer.py         # 遺伝的アルゴリズム最適化
├── report_generator.py  # レポート生成とデータ変換
├── requirements.txt     # 依存関係
├── README.md           # このファイル
├── run_shift_scheduler.bat  # Windows用実行バッチファイル
└── data/               # データファイル
    ├── hope_data.txt   # スタッフ希望シフト
    └── negative.txt    # 相性の悪いペア情報
```


## 🚀 環境構築

### 1. Python環境の準備
Python 3.11以上が必要です。

### 2. 仮想環境の作成
```bash
python -m venv .venv
```

### 3. 仮想環境の有効化
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 4. 依存関係のインストール
```bash
pip install -r requirements.txt
```

## 📊 データファイルの準備

以下のデータファイルを`data/`ディレクトリに配置してください：

- `hope_data.txt`: スタッフの希望シフトデータ
- `negative.txt`: 相性の悪いスタッフペア情報

## 🔧 設定のカスタマイズ

`config.py`で以下の設定を調整できます：

### 基本設定
```python
self.num_staff = 26        # スタッフ数
self.num_days = 7          # 対象日数
self.num_hours = 13        # 営業時間数
```

### 制約設定
```python
self.min_staff_per_hour = 2        # 最小人数
self.max_staff_per_hour = 3        # 最大人数
self.max_work_hours_per_day = 8    # 1日最大労働時間
```

### GA設定
```python
self.population_size = 150         # 個体数
self.generations = 100            # 世代数
self.crossover_prob = 0.8         # 交叉確率
self.mutation_prob = 0.15         # 突然変異確率
```

## 🎮 アプリケーションの実行

### 1. コマンドラインから実行
```bash
python main.py
```

### 2. VS Codeから実行
1. F1キーを押してコマンドパレットを開く
2. "Tasks: Run Task"を選択
3. "Run Shift Scheduler"を選択

### 3. バッチファイルから実行
```bash
run_shift_scheduler.bat
```

## 📈 出力

アプリケーションを実行すると以下が生成されます：

1. **コンソール出力**: 最適化の進捗と結果
2. **進化グラフ**: 最適化の過程を示すグラフ
3. **HTMLレポート**: `shift_report.html`として保存される詳細レポート
4. **DataFrameでのシフト表**: 最適化されたシフト表

## 🔍 機能詳細

### 制約条件
- 人数制約：各時間帯2-3人
- 労働時間制約：1日8時間以下、週40時間以下
- 希望シフトの考慮
- 相性の悪いペアの分離
- 中抜けシフトの回避

### 最適化アルゴリズム
- 遺伝的アルゴリズム（GA）
- スマートな個体生成
- 制約修復オペレータ
- 適応的突然変異

### レポート機能
- HTMLレポート生成
- 進化過程の可視化
- 制約違反の詳細分析
- スタッフ別労働時間統計

## 🧪 開発・テスト

### コード品質ツール
```bash
# コードフォーマット
black *.py

# リンター
flake8 *.py

# テスト実行
pytest
```

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 貢献

プルリクエストやイシューの報告を歓迎します！
