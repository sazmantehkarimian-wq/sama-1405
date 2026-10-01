PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def normalize_digits(value):
    if value is None:
        return ""
    return str(value).translate(PERSIAN_DIGITS).translate(ARABIC_DIGITS)


def normalize_persian_text(value):
    if value is None:
        return ""
    text = normalize_digits(value).strip()
    text = text.replace("ي", "ی").replace("ى", "ی").replace("ك", "ک")
    return " ".join(text.split())


def normalize_space_code(value):
    text = normalize_digits(value).strip()
    if not text.isdigit() or int(text) <= 0:
        raise ValueError("کد فضا باید فقط عدد صحیح مثبت باشد.")
    normalized = str(int(text))
    if normalized != text:
        # Leading zeroes are not accepted because code is the immutable business key.
        raise ValueError("کد فضا نباید صفر ابتدایی داشته باشد.")
    return normalized
