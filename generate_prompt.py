from typing import Optional

def generate_image_prompt(
    art_style: Optional[str] = "Soft color palette, detailed line art in modern animation style",
    gender: Optional[str] = "Female",
    age: Optional[str] = "20 years old",
    eye: Optional[str] = "Red",
    hair: Optional[str] = "Medium wavy hair, caramel brown, with detailed hair accessories",
    pose: Optional[str] = "Gentle hand gestures picking flowers",
    expression: Optional[str] = "Smiling happily, pay attention to the subtle shading of the expression",
    gaze: Optional[str] = "Gently toward the flower held in hand",
    clothing: Optional[str] = "Spring-like floral dress, focusing on flower embroidery and frill details",
    composition: Optional[str] = "Capturing the full body of a child in a flower field while also expressing the surrounding nature in detail",
    scene: Optional[str] = "Relaxed flower field under spring sunshine, with each surrounding flower carefully depicted"
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
    
    prompt_template = """Please generate an image with the following characteristics.
Art style: {art_style}
Gender: {gender}
Age group: {age}
Eye color: {eye}
Hair style/color: {hair}
Person's pose: {pose}
Expression: {expression}
Gaze: {gaze}
Clothing/decoration: {clothing}
Composition: {composition}
Scene or situation: {scene}
soft, faint lines and a light color palette to create a dreamlike and fragile appearance.
"""

    return prompt_template.format(
        art_style=art_style,
        gender=gender,
        age=age,
        eye=eye,
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
        age="20歳",
        hair="美しく長い銀髪、風に吹かれている様子",
        pose="本を読んでいる姿勢",
        scene="図書館の窓際で読書を楽しむ様子"
    )
    print("カスタマイズしたプロンプト:")
    print(custom_prompt)