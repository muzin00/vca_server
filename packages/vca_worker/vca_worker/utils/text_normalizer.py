import re


def normalize_text(text: str) -> str:
    """テキストを正規化.

    正規化ルール:
    1. 小文字化（英字）
    2. 句読点・記号を除去
    3. 空白を正規化（連続空白→単一空白、前後トリム）

    Args:
        text: 入力テキスト

    Returns:
        正規化されたテキスト

    Examples:
        >>> normalize_text("Hello, World!")
        'hello world'
        >>> normalize_text("こんにちは、世界！")
        'こんにちは世界'
        >>> normalize_text("  test   test  ")
        'test test'
    """
    # 小文字化
    text = text.lower()

    # 句読点・記号を除去（日本語の句読点も含む）
    # \w は英数字とアンダースコア、日本語文字も含む
    text = re.sub(r"[^\w\s]", "", text)

    # 空白を正規化
    text = " ".join(text.split())

    return text
