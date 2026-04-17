import unicodedata
import re

def normalize_nfd(text: str) -> str:
    """
    Normalizes text to NFD (Normalization Form D) to ensure Middle Korean 
    characters are correctly decomposed/stored.
    """
    if not text:
        return ""
    return unicodedata.normalize('NFD', text)

def normalize_nfc(text: str) -> str:
    """
    Normalizes text to NFC (Normalization Form C) for display/Modern Korean.
    Note: Middle Korean might look different in NFC depending on font support.
    """
    if not text:
        return ""
    return unicodedata.normalize('NFC', text)

def clean_noise(text: str, remove_tone_marks: bool = False) -> str:
    """
    Cleans general noise. 
    If remove_tone_marks is True, removes Bangjeom (Middle Korean tone marks).
    Bangjeom range in Unicode: U+302E (Left single dot), U+302F (Left double dot).
    """
    text = text.strip()
    
    if remove_tone_marks:
        # \u302e: 〮 (combining left single dot)
        # \u302f: 〯 (combining left double dot)
        text = re.sub(r'[\u302e\u302f]', '', text)
        
    return text

if __name__ == "__main__":
    # Test cases
    sample_text = "우리나라〮말〯싸미〮"  # "나랏말싸미" with tone marks
    
    nfd_text = normalize_nfd(sample_text)
    print(f"NFD: {nfd_text} (len: {len(nfd_text)})")
    
    cleaned = clean_noise(nfd_text, remove_tone_marks=False)
    print(f"Cleaned (Keep Marks): {cleaned}")
    
    no_marks = clean_noise(nfd_text, remove_tone_marks=True)
    print(f"Cleaned (No Marks): {no_marks}")
