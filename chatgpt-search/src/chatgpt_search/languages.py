"""Multilingual support: language detection and stopwords.

Supports the world's top 15 languages by global usage.
"""

import sys
from typing import Optional

# All 15 target languages
TARGET_LANGUAGES = {
    "en", "zh", "hi", "es", "fr", "ar", "bn",
    "pt", "ru", "ja", "de", "ko", "tr", "vi", "it",
}

# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

_langdetect_available: Optional[bool] = None


def _check_langdetect() -> bool:
    """Check if langdetect is importable."""
    global _langdetect_available
    if _langdetect_available is None:
        try:
            import langdetect  # noqa: F401
            _langdetect_available = True
        except ImportError:
            _langdetect_available = False
            print(
                "  Warning: langdetect not available. All messages will be tagged 'en'.",
                file=sys.stderr,
            )
    return _langdetect_available


def detect_language(text: str, min_length: int = 20) -> str:
    """Detect the language of a text string.

    Returns ISO 639-1 language code (e.g., 'en', 'ru', 'zh').
    Falls back to 'en' if:
      - text is too short for reliable detection
      - langdetect is not installed
      - detection fails or confidence is low

    Args:
        text: The text to detect language for.
        min_length: Minimum text length for detection attempt.

    Returns:
        ISO 639-1 language code string.
    """
    if not text or len(text.strip()) < min_length:
        return "en"

    if not _check_langdetect():
        return "en"

    try:
        from langdetect import detect_langs
        from langdetect.lang_detect_exception import LangDetectException

        results = detect_langs(text)
        if results and results[0].prob >= 0.5:
            lang = results[0].lang
            # langdetect uses 'zh-cn'/'zh-tw' -- normalize to 'zh'
            if lang.startswith("zh"):
                return "zh"
            return lang
        return "en"
    except (LangDetectException, Exception):
        return "en"


def detect_language_batch(texts: list[str], min_length: int = 20) -> list[str]:
    """Detect languages for a batch of texts.

    Uses langdetect.DetectorFactory seed for reproducibility.

    Returns list of ISO 639-1 language codes, same length as input.
    """
    if not _check_langdetect():
        return ["en"] * len(texts)

    try:
        from langdetect import DetectorFactory
        DetectorFactory.seed = 0  # Reproducible results
    except ImportError:
        return ["en"] * len(texts)

    return [detect_language(text, min_length) for text in texts]


# ---------------------------------------------------------------------------
# Stopword lists for TF-IDF
# Bundled directly -- no external dependency required.
# Sourced from NLTK stopwords corpus + ISO lists.
# ---------------------------------------------------------------------------

STOPWORDS: dict[str, set[str]] = {
    "en": {
        "a", "about", "above", "after", "again", "against", "all", "am", "an",
        "and", "any", "are", "aren't", "as", "at", "be", "because", "been",
        "before", "being", "below", "between", "both", "but", "by", "can",
        "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does",
        "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
        "from", "further", "get", "got", "had", "hadn't", "has", "hasn't",
        "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
        "here", "here's", "hers", "herself", "him", "himself", "his", "how",
        "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into",
        "is", "isn't", "it", "it's", "its", "itself", "just", "let's", "me",
        "might", "more", "most", "mustn't", "my", "myself", "no", "nor",
        "not", "now", "of", "off", "on", "once", "only", "or", "other",
        "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
        "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
        "so", "some", "such", "than", "that", "that's", "the", "their",
        "theirs", "them", "themselves", "then", "there", "there's", "these",
        "they", "they'd", "they'll", "they're", "they've", "this", "those",
        "through", "to", "too", "under", "until", "up", "us", "very", "was",
        "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't",
        "what", "what's", "when", "when's", "where", "where's", "which",
        "while", "who", "who's", "whom", "why", "why's", "will", "with",
        "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're",
        "you've", "your", "yours", "yourself", "yourselves",
    },
    "ru": {
        "а", "без", "более", "бы", "был", "была", "были", "было", "быть",
        "в", "вам", "вас", "весь", "во", "вот", "все", "всего", "всех",
        "вся", "всё", "вы", "где", "да", "даже", "для", "до", "его", "ее",
        "ей", "ему", "если", "есть", "ещё", "же", "за", "здесь", "и", "из",
        "или", "им", "их", "к", "как", "ко", "когда", "кто", "ли", "либо",
        "мне", "может", "мой", "моя", "мы", "на", "над", "надо", "наш",
        "не", "нее", "нет", "ни", "них", "но", "ну", "о", "об", "однако",
        "он", "она", "они", "оно", "от", "очень", "по", "под", "при",
        "про", "раз", "с", "свой", "свою", "себе", "себя", "сейчас",
        "со", "та", "так", "такой", "там", "те", "тем", "то", "того",
        "тоже", "той", "только", "том", "тот", "ту", "ты", "у", "уж",
        "уже", "хоть", "чего", "чей", "чем", "что", "чтобы", "чье",
        "чья", "эта", "эти", "это", "этого", "этой", "этом", "этот", "я",
        "её", "мне",
    },
    "es": {
        "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como",
        "con", "contra", "cual", "cuando", "de", "del", "desde", "donde",
        "durante", "e", "el", "ella", "ellas", "ellos", "en", "entre", "era",
        "esa", "esas", "ese", "eso", "esos", "esta", "estaba", "estado",
        "estar", "estas", "este", "esto", "estos", "fue", "ha", "hasta",
        "hay", "la", "las", "le", "les", "lo", "los", "mas", "me", "mi",
        "muy", "más", "nada", "ni", "no", "nos", "nosotros", "nuestro",
        "o", "otra", "otras", "otro", "otros", "para", "pero", "por",
        "porque", "que", "quien", "se", "ser", "si", "sin", "sino", "sobre",
        "somos", "son", "soy", "su", "sus", "también", "te", "tengo",
        "ti", "tiene", "todo", "todos", "tu", "tus", "un", "una", "unas",
        "uno", "unos", "usted", "ustedes", "y", "ya", "yo",
    },
    "fr": {
        "a", "ai", "au", "aux", "avec", "c", "ce", "ces", "dans", "de",
        "des", "du", "elle", "en", "est", "et", "eu", "fait", "il", "ils",
        "j", "je", "l", "la", "le", "les", "leur", "leurs", "lui", "m",
        "ma", "mais", "me", "mes", "mon", "même", "n", "ne", "ni", "nos",
        "notre", "nous", "on", "ont", "ou", "par", "pas", "plus", "pour",
        "qu", "que", "qui", "s", "sa", "se", "ses", "si", "son", "sont",
        "sur", "t", "ta", "te", "tes", "ton", "tu", "un", "une", "vos",
        "votre", "vous", "y", "à", "été",
    },
    "de": {
        "aber", "alle", "allem", "allen", "aller", "allerdings", "alles",
        "also", "am", "an", "andere", "anderem", "anderen", "anderer",
        "anderes", "als", "auf", "aus", "auch", "bei", "beim", "bereits",
        "bin", "bis", "bist", "da", "dabei", "dadurch", "dafür", "dagegen",
        "daher", "dahin", "damals", "damit", "danach", "daneben", "dann",
        "daran", "darauf", "daraus", "darf", "darfst", "darin", "darüber",
        "darum", "darunter", "das", "davon", "davor", "dazu", "dein",
        "deine", "deinem", "deinen", "deiner", "dem", "den", "denn", "der",
        "des", "deshalb", "dessen", "die", "dies", "diese", "dieselbe",
        "dieselben", "diesem", "diesen", "dieser", "dieses", "doch", "dort",
        "durch", "dürfen", "ein", "eine", "einem", "einen", "einer",
        "einige", "einigem", "einigen", "einiger", "einiges", "einmal",
        "er", "es", "etwas", "euch", "euer", "eure", "eurem", "euren",
        "eurer", "für", "gegen", "gehen", "geht", "ging", "hab", "habe",
        "haben", "hat", "hatte", "hätte", "hier", "hin", "hinter", "ich",
        "ihm", "ihn", "ihnen", "ihr", "ihre", "ihrem", "ihren", "ihrer",
        "im", "in", "indem", "ins", "ist", "ja", "jede", "jedem", "jeden",
        "jeder", "jedes", "jedoch", "jene", "jenem", "jenen", "jener",
        "jenes", "kann", "kein", "keine", "keinem", "keinen", "keiner",
        "man", "manche", "manchem", "manchen", "mancher", "manchmal",
        "mein", "meine", "meinem", "meinen", "meiner", "mir", "mit",
        "nach", "nachdem", "nachher", "nein", "nicht", "nichts", "noch",
        "nun", "nur", "ob", "oder", "ohne", "sein", "seine", "seinem",
        "seinen", "seiner", "seit", "seitdem", "sich", "sie", "sind", "so",
        "sogar", "solch", "solche", "solchem", "solchen", "solcher",
        "soll", "sollen", "sollte", "sollten", "sondern", "sonst",
        "über", "um", "und", "uns", "unser", "unsere", "unserem",
        "unseren", "unserer", "unter", "viel", "viele", "vielem", "vielen",
        "vielleicht", "vom", "von", "vor", "während", "war", "warum",
        "was", "weder", "weil", "weit", "welch", "welche", "welchem",
        "welchen", "welcher", "wenig", "wenige", "wenn", "wer", "werde",
        "werden", "wie", "wieder", "will", "wir", "wird", "wo", "wollen",
        "worden", "würde", "würden", "zu", "zum", "zur", "zwar",
        "zwischen",
    },
    "pt": {
        "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles",
        "aquilo", "as", "até", "com", "como", "da", "das", "de", "dela",
        "delas", "dele", "deles", "depois", "do", "dos", "e", "ela",
        "elas", "ele", "eles", "em", "entre", "era", "essa", "essas",
        "esse", "esses", "esta", "estas", "este", "estes", "eu", "foi",
        "fomos", "for", "foram", "há", "isso", "isto", "já", "lhe",
        "lhes", "mais", "mas", "me", "meu", "meus", "minha", "minhas",
        "muito", "na", "nas", "no", "nos", "nossa", "nossas", "nosso",
        "nossos", "num", "numa", "não", "nós", "o", "os", "ou", "para",
        "pela", "pelas", "pelo", "pelos", "por", "qual", "quando", "que",
        "quem", "se", "sem", "ser", "seu", "seus", "sua", "suas", "são",
        "só", "também", "te", "tem", "teu", "teus", "tu", "tua", "tuas",
        "tém", "um", "uma", "umas", "uns", "você", "vocês", "vos",
    },
    "it": {
        "a", "abbiamo", "ad", "ai", "al", "alla", "alle", "allo", "anche",
        "ancora", "avere", "aveva", "avete", "che", "chi", "ci", "come",
        "con", "contro", "cui", "da", "dai", "dal", "dall", "dalla",
        "dalle", "dallo", "degli", "dei", "del", "dell", "della", "delle",
        "dello", "di", "dopo", "dove", "e", "ed", "era", "eravamo",
        "eravate", "erano", "fa", "facciamo", "fai", "fanno", "fare",
        "fatto", "fu", "gli", "ha", "hai", "hanno", "ho", "i", "il", "in",
        "io", "l", "la", "le", "lei", "li", "lo", "loro", "lui", "ma",
        "me", "mi", "mia", "mie", "miei", "mio", "molto", "ne", "nei",
        "nel", "nell", "nella", "nelle", "nello", "no", "noi", "non",
        "nostra", "nostre", "nostri", "nostro", "o", "ogni", "per",
        "perché", "più", "poco", "poi", "prima", "quale", "quanta",
        "quante", "quanti", "quanto", "quasi", "quel", "quella", "quelle",
        "quelli", "quello", "questa", "queste", "questi", "questo", "qui",
        "sa", "se", "sei", "si", "sia", "siamo", "siete", "sono", "sotto",
        "sua", "sue", "sui", "sul", "sull", "sulla", "sulle", "sullo",
        "suo", "suoi", "ti", "tra", "tu", "tua", "tue", "tuo", "tuoi",
        "tutti", "tutto", "un", "una", "uno", "vi", "voi", "vostra",
        "vostre", "vostri", "vostro", "è",
    },
    "zh": {
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
        "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你",
        "会", "着", "没有", "看", "好", "自己", "这", "他", "她", "它",
        "们", "那", "把", "这个", "那个", "这些", "那些", "什么", "哪",
        "怎么", "如何", "为什么", "因为", "所以", "但是", "但", "而",
        "或", "如果", "虽然", "只", "又", "再", "还", "已经", "正在",
        "可以", "能", "会", "将", "被", "给", "从", "对", "向", "与",
        "跟", "比", "让", "地", "得", "过",
    },
    "ja": {
        "の", "に", "は", "を", "た", "が", "で", "て", "と", "し", "れ",
        "さ", "ある", "いる", "も", "する", "から", "な", "こと", "として",
        "い", "や", "れる", "など", "なっ", "ない", "この", "ため", "その",
        "あっ", "よう", "また", "もの", "という", "あり", "まで", "られ",
        "なる", "へ", "か", "だ", "これ", "によって", "により", "おり",
        "より", "による", "ず", "なり", "られる", "において", "ば",
        "なかっ", "なく", "しかし", "について", "せ", "だっ", "その他",
        "できる", "それ", "う", "ので", "なお", "のみ", "でき", "き",
        "つ", "における", "お", "ほか", "ほとんど",
    },
    "ko": {
        "이", "그", "저", "것", "수", "들", "등", "를", "에", "의", "가",
        "은", "는", "로", "으로", "와", "과", "도", "에서", "까지",
        "하다", "하고", "한", "있다", "없다", "되다", "이다", "있는",
        "또한", "같은", "그리고", "하는", "또는", "더", "이런", "그런",
        "저런", "아니", "하지", "보다", "때문",
    },
    "ar": {
        "في", "من", "على", "إلى", "عن", "مع", "هذا", "هذه", "ذلك",
        "التي", "الذي", "هو", "هي", "لا", "ما", "كان", "قد", "أن",
        "إن", "بعد", "قبل", "كل", "ذلك", "بين", "عند", "لم", "حتى",
        "إذا", "ثم", "أو", "لكن", "هل", "أي", "غير", "نحن", "هم",
        "أنا", "أنت", "فيها", "منها", "فيه", "منه", "عليه", "عليها",
        "به", "بها", "و", "أيضا", "ولكن",
    },
    "hi": {
        "का", "के", "की", "में", "है", "हैं", "को", "से", "पर", "ने",
        "और", "एक", "यह", "वह", "था", "थी", "थे", "कि", "जो", "तो",
        "हो", "नहीं", "इस", "अपने", "भी", "कर", "या", "हम", "मैं",
        "उस", "वे", "इसके", "उसके", "लिए", "गया", "गई", "जब", "तक",
        "साथ", "कुछ", "दो", "बहुत", "अब", "जा", "आप",
    },
    "tr": {
        "bir", "bu", "da", "de", "ve", "ile", "için", "mi", "mı", "mu",
        "mü", "ama", "ancak", "ben", "sen", "o", "biz", "siz", "onlar",
        "ne", "olan", "var", "yok", "daha", "en", "çok", "her", "gibi",
        "kadar", "sonra", "önce", "üzerinde", "altında", "arasında",
        "değil", "ise", "olarak", "bile", "sadece", "hem", "ya",
    },
    "vi": {
        "và", "của", "là", "có", "được", "cho", "trong", "với", "không",
        "một", "này", "đã", "từ", "như", "những", "các", "để", "về",
        "khi", "theo", "do", "ra", "lên", "cũng", "bị", "tại", "hay",
        "nếu", "đến", "còn", "nhiều", "hoặc", "hơn", "vì", "rất",
        "vào", "trên", "bằng", "nhưng", "mà", "nào", "đó",
    },
    "bn": {
        "এবং", "এই", "একটি", "করা", "করে", "কিন্তু", "যে", "তা",
        "তার", "তাদের", "থেকে", "না", "নিয়ে", "বা", "মধ্যে", "যা",
        "সে", "হয়", "হয়ে", "হলে", "আর", "আমি", "আমরা", "উপর",
        "ও", "কি", "পরে", "বলে", "হতে", "হবে", "এ", "দিয়ে",
    },
}


def get_stopwords(lang: str) -> set[str]:
    """Get stopwords for a language. Returns empty set if language not supported."""
    return STOPWORDS.get(lang, set())


def get_combined_stopwords(langs: set[str]) -> set[str]:
    """Get combined stopwords for multiple languages (union)."""
    combined = set()
    for lang in langs:
        combined.update(get_stopwords(lang))
    return combined


def get_stopwords_list(lang: str) -> list[str]:
    """Get stopwords as a sorted list (for TfidfVectorizer)."""
    return sorted(get_stopwords(lang))


# ---------------------------------------------------------------------------
# Feature support matrix
# ---------------------------------------------------------------------------

def language_feature_matrix() -> dict[str, dict[str, bool]]:
    """Return feature support matrix for all target languages.

    Returns dict mapping lang code to {search: bool, keywords: bool}.
    All languages get search (FTS5 unicode61 handles all scripts).
    Keywords require stopword list.
    """
    matrix = {}
    for lang in sorted(TARGET_LANGUAGES):
        matrix[lang] = {
            "search": True,  # FTS5 unicode61 handles all Unicode
            "keywords": lang in STOPWORDS,
        }
    return matrix


# Language names for display
LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "zh": "Chinese",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "ar": "Arabic",
    "bn": "Bengali",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "de": "German",
    "ko": "Korean",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "it": "Italian",
}
