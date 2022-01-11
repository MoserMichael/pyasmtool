def fac(arg_n):
    if arg_n == 1:
        return arg_n
    return arg_n * fac(arg_n - 1)

print(fac(6))

