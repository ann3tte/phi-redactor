# Re-identify logic
def reidentify_text(text, mapping):
    for key, value in mapping.items():
        text = text.replace(key, value)
    return text

# Converts *LABEL* to correct __LABEL#X__ in order
def convert_starred_to_placeholders(text, mapping):
    new_text = text
    label_lookup = {}
    for key in mapping:
        label = key.split("#")[0].strip("_")
        label_lookup.setdefault(label, []).append(key)

    for label, keys in label_lookup.items():
        count = 0
        while f"*{label}*" in new_text and count < len(keys):
            new_text = new_text.replace(f"*{label}*", keys[count], 1)
            count += 1

    return new_text