import os
import yaml
from typing import Optional, Dict, Any


def load_config_from_yaml(config_path: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """
    YAMLファイルから設定を読み込む関数
    
    Parameters:
    ----------
    config_path : str, optional
        設定ファイルのパス
        
    Returns:
    -------
    Dict[str, Dict[str, str]]
        読み込んだ設定
    """
    # 環境変数から設定ファイルのパスを取得（指定がなければデフォルト）
    if config_path is None:
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
        if preset_name is None:
            preset_name = os.environ.get('PROMPT_PRESET', 'default')

        # デフォルトプリセットが存在しない場合は空の辞書を使用
        if preset_name not in presets:
            preset_config = {}
        else:
            preset_config = presets[preset_name]
        return preset_config
    except Exception as e:
        print(f"Error loading config file: {e}")
        return {"default": {}}