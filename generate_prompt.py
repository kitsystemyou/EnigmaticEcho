from typing import Optional

def generate_image_prompt(
    art_style: Optional[str] = "ソフトな色使いと精細な線画の現代アニメスタイル",
    gender: Optional[str] = "女性",
    age: Optional[str] = "少女",
    hair: Optional[str] = "ミディアムの波打つ髪、キャラメルブラウン、ヘアアクセサリーのディテール",
    pose: Optional[str] = "花を摘むやさしい手つき",
    expression: Optional[str] = "幸せそうに微笑む、表情の細かい陰影に注意",
    gaze: Optional[str] = "手に持った花へと優しく",
    clothing: Optional[str] = "春らしいフローラルドレス、花の刺繍とフリルのディテールに注目",
    composition: Optional[str] = "花畑にいる子供の全身を捉えつつ、周囲の自然も精細に表現",
    scene: Optional[str] = "春の日差しのもとでのびのびとした花畑、周りの花々も一つ一つ丁寧に描写"
) -> str:
    """
    画像生成のプロンプトを作成する関数
    
    Parameters:
    ----------
    art_style : str, optional
        画風の説明
    gender : str, optional
        性別
    age : str, optional
        年齢層
    hair : str, optional
        髪型・色の説明
    pose : str, optional
        ポーズの説明
    expression : str, optional
        表情の説明
    gaze : str, optional
        視線の説明
    clothing : str, optional
        服装・装飾の説明
    composition : str, optional
        構図の説明
    scene : str, optional
        シーンや状況の説明
    
    Returns:
    -------
    str
        生成されたプロンプト文章
    """
    
    prompt_template = """次の特徴を持つ画像を生成してください。
画風: {art_style}
性別: {gender}
年齢層: {age}
髪型・色: {hair}
人物のポーズ: {pose}
表情: {expression}
視線: {gaze}
服装・装飾: {clothing}
構図: {composition}
シーンや状況: {scene}"""
    
    return prompt_template.format(
        art_style=art_style,
        gender=gender,
        age=age,
        hair=hair,
        pose=pose,
        expression=expression,
        gaze=gaze,
        clothing=clothing,
        composition=composition,
        scene=scene
    )

# 使用例
if __name__ == "__main__":
    # デフォルトの設定で生成
    default_prompt = generate_image_prompt()
    print("デフォルトのプロンプト:")
    print(default_prompt)
    print("\n" + "="*50 + "\n")
    
    # カスタマイズした設定で生成
    custom_prompt = generate_image_prompt(
        art_style="水彩画風のやわらかいタッチ",
        age="青年",
        hair="短い黒髪",
        pose="本を読んでいる姿勢",
        scene="図書館の窓際で読書を楽しむ様子"
    )
    print("カスタマイズしたプロンプト:")
    print(custom_prompt)