import re


def html_to_text(html):
    """
    remove tags, clear and replace unicode escape
    """
    html = str(html)
    cleaned = html.strip()
    # First we remove inline CSS:
    cleaned = re.sub(r"(?is)<(style).*?>.*?(</\1>)", u"", cleaned)
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", u"", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", u" ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", u" ", cleaned)
    cleaned = re.sub(r"\xa0", u" ", cleaned)
    cleaned = re.sub(r"\u2009", u" ", cleaned)
    cleaned = re.sub(r"  ", u" ", cleaned)
    cleaned = re.sub(r"  ", u" ", cleaned)
    return cleaned.strip()


def strip_nlts(s):
    """
    clean spaces
    """
    cleaned = re.sub(r"[\r\n\t]+", u" ", s)
    cleaned = re.sub(r"  ", u" ", cleaned)
    cleaned = re.sub(r"  ", u" ", cleaned)
    return cleaned.strip()
