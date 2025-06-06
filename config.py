import os
import yaml
from typing import Optional, Dict, Any


def load_config_from_yaml() -> Dict[str, Any]:
    """
    YAMLファイルから設定を読み込む関数

    Returns:
    -------
    Dict[str, Any]
        読み込んだ設定
        yamlの型がまだ今後変わる可能性があるのでいったん Any にしておく

    TODO: 中身の tweet_text や prompt のキーが無かったらエラーにする
    """
    # 環境変数から設定ファイルのパスを取得（指定がなければデフォルト）
    config_path = os.environ.get('PROMPT_CONFIG_PATH', 'prompt_config.yaml')
    
    # 設定ファイルが存在するか確認
    if not os.path.exists(config_path):
        print(f"Warning: Config file '{config_path}' not found. Using default settings.")
        return {"default": {}}
    
    # YAMLファイルを読み込む
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)

        # 環境変数からプリセット名を取得（指定がなければデフォルト）
        preset_name = os.environ.get('PROMPT_PRESET', 'default')
        preset_config = config.get(preset_name)

        # 値が存在しないまたは空の場合は空の辞書を使用
        if not preset_config:
            raise ValueError("preset_config が空または存在しません")
        return preset_config
    except Exception as e:
        print(f"Error loading config file: {e}")
        return {"default": {}}