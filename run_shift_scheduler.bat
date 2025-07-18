@echo off
echo ==========================================
echo    シフト自動生成システム（リファクタリング版）
echo ==========================================
echo.

echo 仮想環境をアクティベート中...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo エラー: 仮想環境が見つかりません
    echo まず 'python -m venv .venv' を実行してください
    pause
    exit /b 1
)

echo 依存関係をチェック中...
python -c "import pandas, numpy, matplotlib, deap" 2>nul
if errorlevel 1 (
    echo エラー: 必要なライブラリがインストールされていません
    echo 'pip install -r requirements.txt' を実行してください
    pause
    exit /b 1
)

echo.
echo アプリケーションを起動中...
echo.
python main.py

echo.
echo ==========================================
echo 実行完了！
echo HTMLレポートが生成されました: shift_report.html
echo ==========================================
echo.
pause
