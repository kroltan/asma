#!/usr/bin/env python
import argparse

from pyparsing import Group, Word, Literal, Optional, alphanums, alphas, nums, restOfLine


def bnf():
    comment = "#" + restOfLine
    variable_name = Word(alphas, alphanums)
    literal = Word(nums)
    operator = Word("+-|&", max=1)
    comparsion = Literal("<") | ">" | "==" | "<=" | ">=" | "!="

    variable_reference = "@" + variable_name("address")
    literal_reference = "@" + literal("address")

    value = Group(variable_reference | variable_name | literal_reference | literal)
    operation = Group(value("val") | (value("lhs") + operator("op") + value("rhs")))

    command = variable_name("name") + "=" + operation("value")
    goto = "goto" + variable_name("target") + Optional("if" + value("lhs") + comparsion("comp") + value("rhs"))

    return (command | goto).ignore(comment)


def asm(string, *args, **kwargs):
    return "\n".join(line.strip() for line in string.split("\n")).format(*args, **kwargs)


def process_command(stmt):
    if stmt.value.val:
        val = stmt.value.val
        if val.address:
            return asm("""
                @{address}
                D=A
                @{name}
                M=D
            """, address=val.address, name=stmt.name)
    return ""


def process_jump(stmt):
    return ""


def translate_asm(parser, line):
    stmt = parser.parseString(line)
    if stmt.name:
        return process_command(stmt)
    elif stmt.target:
        return process_jump(stmt)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("input", help="file to run")
    args = argparser.parse_args()

    parser = bnf()
    with open(args.input) as f:
        print "\n".join(translate_asm(parser, line) for line in f)


if __name__ == '__main__':
    main()
