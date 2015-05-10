#!/usr/bin/env python
import argparse

from pyparsing import Group, Word, Literal, Optional, \
                      alphanums, alphas, nums, restOfLine, \
                      Empty, Suppress


def bnf():
    comment = "#" + restOfLine
    variable_name = Word(alphas, alphanums+"_")
    literal = Word(nums)
    operator = Word("+-|&", max=1)
    comparsion = Literal("!=") | "<=" | "<" | ">=" | ">" | "=="

    variable_reference = Suppress("@") + variable_name("address")
    literal_reference = Suppress("@") + literal("address")

    value = Group(variable_reference
                  | variable_name
                  | literal_reference
                  | literal)
    operation = ((value("lhs") + operator("op") + value("rhs"))
                 | Group("-" + value("negative_val"))
                 | value("val"))

    command = value("name") + Suppress("=") + operation("value")
    goto = (Suppress("goto") + variable_name("target")
            + Optional(Suppress("if")
                       + operation("value") + comparsion("cmp")
                       + Suppress("0")
                       + Optional(Suppress("else")
                                  + variable_name("elsetgt"))))
    label = value("anchor") + Suppress(":")

    return (command | label | goto | Empty()).ignore(comment)


def asm(string, *args, **kwargs):
    return "\n".join(
        line.strip() for line in string.split("\n") if line
    ).format(*args, **kwargs).strip()


def getvar(value, name=None):
    val = value.address or value[0]
    isnum = type(val) is str and val.isdecimal()
    kind = "A" if isnum or value.address else "M"
    prefix = name + "_" if name else ""
    return {prefix + "address": val, prefix + "kind": kind}


def process_command(stmt):
    destination = getvar(stmt.name)
    indirection = "A=M" if destination["kind"] is "A" else ""
    if stmt.op:
        variables = getvar(stmt.lhs, name="lhs")
        variables.update(getvar(stmt.rhs, name="rhs"))

        return asm("""
            @{lhs_address}
            D={lhs_kind}
            @{rhs_address}
            D={rhs_kind}{op}D
            @{name}
            {ind}
            M=D
        """,
                   ind=indirection,
                   op=stmt.op,
                   name=destination["address"],
                   **variables)
    elif stmt.value.negative_val:
        val = getvar(stmt.value.negative_val)
        if destination["address"] == val["address"]:
            return asm("""
                @{name}
                {ind}
                M=-{kind}
            """, ind=indirection, name=destination["address"], **val)
        else:
            return asm("""
                @{address}
                D=-{kind}
                @{name}
                {ind}
                M=D
            """, ind=indirection, name=destination["address"], **val)
    else:
        val = getvar(stmt.value)
        if val["kind"] == "A" and val["address"] in ("1", "0", "-1"):
            return asm("""
                @{name}
                {ind}
                M={val}
            """,
                       ind=indirection,
                       name=destination["address"],
                       val=val["address"])
        else:
            return asm("""
                @{address}
                D={kind}
                @{name}
                {ind}
                M=D
            """,
                       ind=indirection,
                       name=destination["address"],
                       **getvar(stmt.value))

    return ""


def process_jump(stmt):
    if stmt.cmp:
        operations = {
            "<": "JLT",
            ">": "JGT",
            "==": "JEQ",
            "<=": "JLE",
            ">=": "JGE",
            "!=": "JNE",
            "": "JMP"
        }
        elsejmp = asm("""
            @{target}
            0;JMP
        """, target=stmt.elsetgt) if stmt.elsetgt else ""
        if stmt.val:
            var = getvar(stmt.val)
            return asm("""
                @{address}
                D={kind}
                @{target}
                D;{cmp}
            """,
                       cmp=operations[stmt.cmp],
                       target=stmt.target,
                       **var)
        elif stmt.negative_val:
            var = getvar(stmt.value.negative_val)
            return asm("""
                @{address}
                D=-{kind}
                @{target}
                D;{cmp}
            """,
                       cmp=operations[stmt.cmp],
                       target=stmt.target,
                       **var)
        else:
            sides = getvar(stmt.lhs, name="lhs")
            sides.update(getvar(stmt.rhs, name="rhs"))
            return asm("""
                @{lhs_address}
                D={lhs_kind}
                @{rhs_address}
                D={rhs_kind}{op}D
                @{target}
                D;{cmp}
                {elsejmp}
            """,
                       cmp=operations[stmt.cmp],
                       target=stmt.target,
                       op=stmt.op,
                       elsejmp=elsejmp,
                       **sides)
    else:
        return asm("""
            @{target}
            0;JMP
        """, target=stmt.target)


def process_anchor(stmt):
    return asm("""
        ({anchor})
    """, anchor=stmt.anchor[0])


def translate_asm(parser, line):
    stmt = parser.parseString(line)
    if stmt.name:
        new = process_command(stmt)
    elif stmt.target:
        new = process_jump(stmt)
    elif stmt.anchor:
        new = process_anchor(stmt)
    else:  # is a comment
        if len(line) >= 2:
            return "//" + line[1:].strip()
        else:
            return ""
    return "//{line}\n{new}\n".format(line=line.strip(), new=new)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("input", help="file to run")
    args = argparser.parse_args()

    parser = bnf()
    with open(args.input) as f:
        translated = (translate_asm(parser, line) for line in f if line)
        cleanup = (line for line in translated if line)
        print("\n".join(cleanup))


if __name__ == '__main__':
    main()
