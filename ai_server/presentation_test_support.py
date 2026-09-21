"""Locate public output sections without tying data checks to obsolete page numbers.

Section-order/count assertions remain in the public contract tests. These helpers
fail on missing or duplicate matches, so moving a section cannot silently skip a
chart, table, source or numeric assertion.
"""


def slide_with_title(deck, title):
    matches = [slide for slide in deck.slides if any(
        shape.name == 'title' and shape.has_text_frame and shape.text == title
        for shape in slide.shapes)]
    if len(matches) != 1:
        raise AssertionError(f'Expected one section {title!r}, found {len(matches)}')
    return matches[0]


def named_shape(slide, name):
    matches = [shape for shape in slide.shapes if shape.name == name]
    if len(matches) != 1:
        raise AssertionError(f'Expected one shape {name!r}, found {len(matches)}')
    return matches[0]
