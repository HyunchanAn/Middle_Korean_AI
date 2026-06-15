import pytest
from src.preprocess.filter_noise import is_hanja_heavy, has_modern_keywords

def test_is_hanja_heavy_false():
    text = "나랏말싸미 듕귁에 달아 문자와로 서르 사맛디 아니할쎄"
    assert not is_hanja_heavy(text, threshold=0.15)

def test_is_hanja_heavy_true():
    # 韓國獨立運動史 (7 hanja chars)
    text = "韓國獨立運動史"
    assert is_hanja_heavy(text, threshold=0.15)
    
    # Mixed text (2 hanja out of 10 non-space characters = 20%)
    mixed_text = "이 문서는 報告서입니다"
    assert is_hanja_heavy(mixed_text, threshold=0.15)

def test_is_hanja_heavy_empty():
    assert not is_hanja_heavy("")
    assert not is_hanja_heavy("   \n  ")

def test_has_modern_keywords_false():
    text = "나랏말싸미 듕귁에 달아 문자와로 서르 사맛디 아니할쎄"
    assert not has_modern_keywords(text)

def test_has_modern_keywords_true():
    assert has_modern_keywords("총리대신 이완용이 報告를 올리다")
    assert has_modern_keywords("隆熙 4년에 일어난 일")
    assert has_modern_keywords("재판소에서 裁判이 열렸다")
