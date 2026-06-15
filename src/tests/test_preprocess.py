import pytest
import unicodedata
from src.preprocess.normalize import normalize_nfd, normalize_nfc, clean_noise

def test_normalize_nfd():
    text = "나랏말싸미"
    nfd_text = normalize_nfd(text)
    assert nfd_text == unicodedata.normalize('NFD', text)
    assert len(nfd_text) > len(text)  # NFD decomposes composite characters

def test_normalize_nfc():
    nfd_text = unicodedata.normalize('NFD', "나랏말싸미")
    nfc_text = normalize_nfc(nfd_text)
    assert nfc_text == unicodedata.normalize('NFC', nfd_text)
    assert len(nfc_text) < len(nfd_text)  # NFC composes characters back

def test_clean_noise_keep_marks():
    text = "말\u302e싸미\u302f"  # Text with Bangjeom (tone marks)
    cleaned = clean_noise(text, remove_tone_marks=False)
    assert "\u302e" in cleaned
    assert "\u302f" in cleaned
    assert cleaned == text

def test_clean_noise_remove_marks():
    text = "말\u302e싸미\u302f"  # Text with Bangjeom (tone marks)
    cleaned = clean_noise(text, remove_tone_marks=True)
    assert "\u302e" not in cleaned
    assert "\u302f" not in cleaned
    assert cleaned == "말싸미"

def test_clean_noise_strip():
    text = "  나랏말싸미  "
    assert clean_noise(text) == "나랏말싸미"
