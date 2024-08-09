import re


class Parser:
    def __init__(self, func):
        self.func = func

    def __call__(self, text, pos=0):
        return self.func(text, pos)

    def __repr__(self):
        return f"Parser({self.func.__name__})"


# Combines two parsers
def seq(parser1, parser2):
    def parse_seq(s, idx):
        x, idx2 = parser1(s, idx)
        y, idx3 = parser2(s, idx2)
        if x is None or y is None:
            return (None, idx)
        return ((x, y), idx3)

    return Parser(parse_seq)


# Returns the result of the first parser that succeeds
def choice(parser1, parser2):
    def parse_choice(s, idx):
        x = parser1(s, idx)
        if x[0] is not None:
            return x
        return parser2(s, idx)

    return Parser(parse_choice)


# Returns the result of the second parser if the first parser succeeds
def compose(parser1, parser2):
    def parse_compose(s, idx):
        x, idx2 = parser1(s, idx)
        if x is None:
            return (None, idx)
        return parser2(s, idx2)

    return Parser(parse_compose)


# Returns the result of the second parser if the first, second and third parser succeed
def between(parser1, parser2, parser3):
    def parse_between(s, idx):
        x, idx2 = parser1(s, idx)
        if x is None:
            return (None, idx)
        y, idx3 = parser2(s, idx2)
        if y is None:
            return (None, idx)
        z, idx4 = parser3(s, idx3)
        if z is None:
            return (None, idx)

        return (y, idx3)

    return Parser(parse_between)


# Returns the result of the first parser with a function applied to it
def fmap(f, parser):
    def parse_fmap(s, idx):
        x = parser(s, idx)
        if x[0] is None:
            return (None, idx)
        return (f(x), x[1])
    return Parser(parse_fmap)


# Returns the result of the first parser if it matches the regex pattern
def regex(regex_str):
    compiled_re = re.compile(regex_str)
    def inner(s, idx):
        match = compiled_re.match(s, idx)
        if match:
            return match.group(0), match.end()
        else:
            return (None, idx)

    return inner


# Returns what is passed to it
def pure(x):
    def inner(s, idx):
        return x, idx

    return Parser(inner)


# Returns the result of the parser after applying the function that turns the result of the first parser into a parser, then using that parser to parse the rest of the string
def bind(parser, f):
    def inner(s, idx):
        x, idx2 = parser(s, idx)
        if x is None:
            return (None, idx)
        return f(x)(s, idx2)

    return Parser(inner)


# Returns a list of the results of the first parser until failure
def many(parser):
    def inner(s, idx):
        result = []
        while True:
            x, idx2 = parser(s, idx)
            if x is None:
                break
            result.append(x)
            idx = idx2
        return result, idx
    return Parser(inner)

def parse_a(text, pos):
    if pos < len(text) and text[pos] == "a":
        return "a", pos + 1
    return (None, pos)


def parse_true(text, pos):
    if text.startswith("true", pos):
        return "true", pos + 4
    return (None, pos)


def parse_false(text, pos):
    if text.startswith("false", pos):
        return "false", pos + 5
    return (None, pos)


parse_letter_a = Parser(parse_a)
parse_true = Parser(parse_true)

# Parse combined PC
parse_combined = seq(parse_letter_a, parse_true)

result = parse_combined("atrue", 0) # Expected output: (('a', 'true'), 5)
print(result)

# Parse choice PC
parse_or = choice(parse_letter_a, parse_true)

result = parse_or("atrue", 0) # Expected output: ('a', 1)
print(result)

# Parse compose PC
parse_skip = compose(parse_letter_a, parse_true)

result = parse_skip("atrue", 0) # Expected output: ('true', 5)
print(result)

# Parse between PC
parse_between = between(parse_letter_a, parse_true, parse_false)

result = parse_between("atruefalse", 0) # Expected output: ('true', 5)
print(result)

# Parse fmap PC
parse_fmap = fmap(lambda x: "".join(map(str, x)), parse_letter_a)

result = parse_fmap("abc", 0) # Expected output: ('a1', 1)
print(result)

# Parse regex
parse_regex = regex(r"\d+")

result = parse_regex("123", 0) # Expected output: (123, 3)
print(result)  # NOQA

# Parse pure
parse_pure = pure("a")

result = parse_pure("abc", 0) # Expected output: ('a', 0)
print(result)

# Parse bind
parse_bind = bind(parse_letter_a, lambda x: pure(x + "b"))

result = parse_bind("a", 0) # Expected output: ('ab', 1)
print(result)

# Parse many
parse_many = many(parse_letter_a)

result = parse_many("aaab", 0) # Expected output: (['a', 'a', 'a'], 3)
print(result)
