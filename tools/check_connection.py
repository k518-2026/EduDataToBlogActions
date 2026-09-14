"""
Diagnostic Tool for WordPress & SMTP Connection.
Runs checks on environment variables, SMTP authentication, and optional test email.
"""
import logging
import os
import smtplib
import sys
from email.mime.text import MIMEText
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("ConnectionChecker")


def check_env_variables():
    logger.info("==================================================")
    logger.info("🔍 1. 環境変数・シークレットの設定確認")
    logger.info("==================================================")

    vars_to_check = {
        "WP_POST_EMAIL": os.getenv("WP_POST_EMAIL", ""),
        "SMTP_USER": os.getenv("SMTP_USER", ""),
        "SMTP_PASS": os.getenv("SMTP_PASS", ""),
        "SMTP_HOST": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
    }

    has_error = False
    for name, val in vars_to_check.items():
        if not val:
            if name in ("WP_POST_EMAIL", "SMTP_USER", "SMTP_PASS"):
                logger.error(f"❌ 【未設定】 {name} が設定されていません。")
                has_error = True
            else:
                logger.warning(f"⚠️ 【未設定（任意）】 {name}")
        else:
            masked = val[:3] + "..." + val[-2:] if len(val) > 6 else "***"
            logger.info(f"✅ {name}: 設定済み ({masked})")

    return not has_error


def check_smtp_connection():
    logger.info("\n==================================================")
    logger.info("📧 2. SMTP サーバー接続・認証テスト")
    logger.info("==================================================")

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "").replace(" ", "")  # Strip spaces in app password

    if not smtp_user or not smtp_pass:
        logger.error("❌ SMTP_USER または SMTP_PASS がないため、接続テストをスキップします。")
        return False

    logger.info(f"サーバー {smtp_host}:{smtp_port} への接続を試行中...")
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            logger.info("TLSハンドシェイク成功。ログインを試行中...")
            server.login(smtp_user, smtp_pass)
            logger.info("🎉 SMTP 認証に成功しました！アカウントとアプリパスワードは正常です。")
            return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ 認証失敗 (SMTPAuthenticationError): {e}")
        logger.error("\n【考えられる原因と対処法】")
        logger.error("1. Gmailの通常のログインパスワードを使っていませんか？")
        logger.error("   → Googleアカウントの「2段階認証」を有効にし、「アプリ パスワード (16桁)」を発行して設定してください。")
        logger.error("2. アプリパスワードの入力ミスや前後の不要な空白がありませんか？")
        return False
    except Exception as e:
        logger.error(f"❌ 接続エラー: {e}")
        return False


def send_test_email():
    logger.info("\n==================================================")
    logger.info("🚀 3. WordPress 投稿用テストメール送信")
    logger.info("==================================================")

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "").replace(" ", "")
    wp_email = os.getenv("WP_POST_EMAIL", "")

    if not wp_email:
        logger.error("❌ WP_POST_EMAIL が未設定のため送信できません。")
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

    logger.info(f"送信先: {wp_email}")
    logger.info(f"送信元: {smtp_user}")
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info("🎉 テストメールを正常に送信しました！")
        logger.info("数分後、WordPress管理画面の「投稿」＞「投稿一覧」または「下書き」をご確認ください。")
        return True
    except Exception as e:
        logger.error(f"❌ メール送信に失敗しました: {e}")
        return False


def main():
    logger.info("🛠️ WordPress & SMTP 接続診断ツールを開始します")
    env_ok = check_env_variables()
    if not env_ok:
        logger.error("\n❌ 必須の環境変数が不足しています。設定を見直してください。")
        sys.exit(1)

    smtp_ok = check_smtp_connection()
    if not smtp_ok:
        logger.error("\n❌ SMTP認証に失敗したため、テスト送信を中止します。")
        sys.exit(1)

    if "--send-test" in sys.argv:
        send_test_email()
    else:
        logger.info("\n💡 実際にWordPressへテスト記事を1通送信して検証したい場合は、")
        logger.info("   python -m tools.check_connection --send-test")
        logger.info("   を実行してください。")


if __name__ == "__main__":
    main()
