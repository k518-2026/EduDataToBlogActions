"""
Diagnostic Tool for WordPress & SMTP Connection.
Runs checks on environment variables, SMTP authentication, and optional test email.
Outputs directly to console and GitHub Step Summary for instant diagnosis.
"""
import logging
import os
import smtplib
import sys
from email.mime.text import MIMEText
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("ConnectionChecker")

summary_lines = []


def add_summary(text: str):
    logger.info(text)
    summary_lines.append(text)


def write_github_summary():
    summary_file = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_file:
        try:
            with open(summary_file, "a", encoding="utf-8") as f:
                f.write("\n".join(summary_lines) + "\n")
        except Exception as e:
            logger.warning(f"Failed to write GITHUB_STEP_SUMMARY: {e}")


def check_env_variables():
    add_summary("## 🔍 1. GitHub Secrets / 環境変数の設定確認")
    add_summary("| 項目名 | 設定状況 | 状態 |")
    add_summary("| :--- | :--- | :---: |")

    vars_to_check = {
        "WP_POST_EMAIL": os.getenv("WP_POST_EMAIL", ""),
        "SMTP_USER": os.getenv("SMTP_USER", ""),
        "SMTP_PASS": os.getenv("SMTP_PASS", ""),
        "SMTP_HOST": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
    }

    missing_required = []
    for name, val in vars_to_check.items():
        if not val:
            if name in ("WP_POST_EMAIL", "SMTP_USER", "SMTP_PASS"):
                add_summary(f"| `{name}` | **未設定 (空)** | ❌ 必須 |")
                missing_required.append(name)
            else:
                add_summary(f"| `{name}` | 未設定（デフォルト/任意） | ⚠️ 任意 |")
        else:
            masked = val[:3] + "..." + val[-2:] if len(val) > 6 else "***"
            add_summary(f"| `{name}` | 設定済み (`{masked}`) | ✅ 正常 |")

    if missing_required:
        add_summary("\n> [!CAUTION]")
        add_summary(f"> 必須のSecret ({', '.join(missing_required)}) が設定されていません！")
        add_summary("> リポジトリの **Settings ＞ Secrets and variables ＞ Actions** にて登録してください。\n")
        return False
    return True


def check_smtp_connection():
    add_summary("## 📧 2. SMTP サーバー接続・認証テスト")

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "").replace(" ", "")

    if not smtp_user or not smtp_pass:
        add_summary("❌ `SMTP_USER` または `SMTP_PASS` が未設定のため、接続テストをスキップします。")
        return False

    add_summary(f"- 接続先サーバー: `{smtp_host}:{smtp_port}`")
    add_summary(f"- ログインユーザー: `{smtp_user}`")

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            add_summary("\n> [!TIP]")
            add_summary("> **🎉 SMTP認証（Gmailログイン）に成功しました！**")
            add_summary("> 送信元アカウントおよびアプリパスワードは完全に正常です。\n")
            return True
    except smtplib.SMTPAuthenticationError as e:
        add_summary("\n> [!CAUTION]")
        add_summary(f"> **❌ SMTP認証に失敗しました (Authentication Failed):** `{e}`")
        add_summary("> ")
        add_summary("> **【原因と対処法】**")
        add_summary("> 1. **通常のGoogleログインパスワードを使っていませんか？**")
        add_summary(">    Googleアカウント設定 ＞ セキュリティ ＞ 2段階認証 ＞ **「アプリ パスワード (16桁)」** を発行して設定してください。")
        add_summary("> 2. **アプリパスワードの入力ミスはありませんか？**")
        add_summary(">    空白スペースを抜いた16桁英字で登録し直してください。\n")
        return False
    except Exception as e:
        add_summary(f"\n❌ 接続時エラー: `{e}`\n")
        return False


def send_test_email():
    add_summary("## 🚀 3. WordPress 投稿用テストメール送信結果")

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "").replace(" ", "")
    wp_email = os.getenv("WP_POST_EMAIL", "")

    if not wp_email:
        add_summary("❌ `WP_POST_EMAIL` が未設定のため送信できません。")
        return False

    msg = MIMEText(
        "<p>これは EduDataToBlogActions の接続診断テスト投稿です。</p>"
        "<p>この投稿がWordPress上に表示されれば、メール投稿パイプラインは正常に機能しています。</p>",
        "html",
        "utf-8",
    )
    msg["Subject"] = "【接続テスト】EduDataToBlogActions 投稿確認"
    msg["From"] = smtp_user
    msg["To"] = wp_email

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        add_summary("\n> [!TIP]")
        add_summary("> **🎉 WordPress投稿用メールの送信に成功しました！**")
        add_summary(f"> 送信先: `{wp_email}` / 送信元: `{smtp_user}`")
        add_summary("> 数分後、WordPress管理画面の「投稿一覧」または「下書き」をご確認ください。\n")
        return True
    except Exception as e:
        add_summary(f"\n❌ メール送信エラー: `{e}`\n")
        return False


def main():
    add_summary("# 🛠️ WordPress & SMTP 接続診断レポート\n")

    env_ok = check_env_variables()
    if not env_ok:
        write_github_summary()
        sys.exit(1)

    smtp_ok = check_smtp_connection()
    if not smtp_ok:
        write_github_summary()
        sys.exit(1)

    if "--send-test" in sys.argv:
        mail_ok = send_test_email()
        if not mail_ok:
            write_github_summary()
            sys.exit(1)

    write_github_summary()


if __name__ == "__main__":
    main()
