from uuid import UUID

import pyparsing
from pyparsing import Word, Literal, hexnums

irc_name = (
    pyparsing.Word(
        initChars=pyparsing.alphas,
        bodyChars=pyparsing.alphanums + "[]{}|:-_<>\\/",
    )
) + pyparsing.WordEnd()
"""
Matches a valid IRC nickname.
 Token MUST start with a letter but MAY contain numerics and some special chars
"""

api_id = pyparsing.Optional(pyparsing.Suppress("@")) + (
    Word(hexnums, exact=8)
    + Literal("-")
    + Word(hexnums, exact=4)
    + Literal("-")
    + Word(hexnums, exact=4)
    + Literal("-")
    + Word(hexnums, exact=4)
    + Literal("-")
    + Word(hexnums, exact=12)
    + pyparsing.WordEnd()
).setParseAction(lambda tokens: UUID("".join(tokens.asList())))
""" matches a well formed UUID4"""

case_number = (
    # may lead with 'case'
    api_id
    | pyparsing.Optional(pyparsing.Literal("#").suppress())
    + pyparsing.Word(pyparsing.nums).setParseAction(lambda token: int(token[0]))
) + pyparsing.WordEnd()
"""Matches a case number"""

rescue_identifier = irc_name | case_number
"""Matches any valid rescue identifier, converting matches to their corresponding types. """

suppress_first_word = pyparsing.Word(pyparsing.printables).suppress()
""" Suppresses the first word in the string. """

timer = pyparsing.Word(pyparsing.nums) + ":" + pyparsing.Word(pyparsing.nums) + pyparsing.WordEnd()
""" matches something that looks like a timer. `d:d` """

platform = (
    pyparsing.CaselessKeyword("pc").setResultsName("pc")
    | (
        pyparsing.CaselessKeyword("ps")
        ^ pyparsing.CaselessKeyword("ps")
        ^ pyparsing.CaselessKeyword("ps4")
        ^ pyparsing.CaselessKeyword("playstation")
        ^ pyparsing.CaselessKeyword("playstation4")
        ^ pyparsing.CaselessKeyword("playstation 4")
    ).setResultsName("playstation")
    | (
        pyparsing.CaselessLiteral("xb")
        ^ pyparsing.CaselessLiteral("xb1")
        ^ pyparsing.CaselessLiteral("xbox")
        ^ pyparsing.CaselessLiteral("xboxone")
        ^ pyparsing.CaselessLiteral("xbox one")
    ).setResultsName("xbox")
) + pyparsing.WordEnd()
"""
Matches a platform specifier
"""

rest_of_line = pyparsing.restOfLine.setParseAction(lambda token: token[0].strip())
""" Captures all remaining text, stripping leading/trailing whitespace."""
