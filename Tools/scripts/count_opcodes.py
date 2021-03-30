import opcode
import os
import sys

OF_INTEREST_NAMES = ["POP_JUMP_IF_NONE", "POP_JUMP_IF_NOT_NONE"]

of_interest = set(opcode.opmap[x] for x in OF_INTEREST_NAMES)


def all_code_objects(code):
    yield code
    for x in code.co_consts:
        if hasattr(x, 'co_code'):
            yield x


def report(code, filename):
    of_interest_count = total_count = 0
    for co in all_code_objects(code):
        co_code = co.co_code
        for i in range(0, len(co_code), 2):
            op = co_code[i]
            if op in of_interest:
                of_interest_count += 1
            else:
                total_count += 1
    if of_interest_count:
        print(filename + ":", of_interest_count, "/", total_count,
              f"{of_interest_count/total_count*100:.2f}%")
    return of_interest_count, total_count


def get_code(filename):
    try:
        with open(filename) as f:
            source = f.read()
        code = compile(source, filename, "exec")
        return code
    except Exception as err:
        print(filename + ":", err, file=sys.stderr)
        return None


def main(filename):
    print("OF INTEREST:", ", ".join(OF_INTEREST_NAMES))
    of_interest_count = total_count = 0
    if not os.path.isdir(filename):
        code = get_code(filename)
        if code is None:
            sys.exit(1)
        of_interest_count, total_count = report(code, filename)
    else:
        for root, dirs, files in os.walk(filename):
            for file in files:
                if file.endswith(".py"):
                    full = os.path.join(root, file)
                    code = get_code(full)
                    if code is None:
                        continue
                    a, b = report(code, full)
                    of_interest_count += a
                    total_count += b
    if total_count:
        print("TOTAL", of_interest_count, "/", total_count,
              f"{of_interest_count/total_count*100:.2f}%")
    else:
        print("TOTAL", of_interest_count, "/", total_count)


if __name__ == "__main__":
    main(sys.argv[1])
