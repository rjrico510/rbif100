#!/usr/bin/env python3



def lowerA(str) -> str:
    """converts A->a in a string

    Args:
        str (str):input string

    Returns:
        str: output string with all A's converted to a's
    """
    return str.replace('A', 'a')


def main():
    """convert to upper
    """
    str = 'ATCGATCGCGTA'
    result = lowerA(str)
    print(f'in: {str} out: {result}')

if __name__ =='__main__':
    main()