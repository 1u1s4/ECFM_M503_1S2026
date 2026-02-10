#!/usr/bin/env python3
"""
Lee un array desde `input.txt`, lo ordena usando quicksort y imprime el resultado.

Formato de `input.txt`: números enteros separados por espacios, comas o saltos de línea.
Ejemplo: 8 3 1 7 0 10 2 5
"""
import os
import re
import sys


def quicksort(arr):
	if len(arr) <= 1:
		return arr
	pivot = arr[len(arr) // 2]
	left = [x for x in arr if x < pivot]
	mid = [x for x in arr if x == pivot]
	right = [x for x in arr if x > pivot]
	return quicksort(left) + mid + quicksort(right)


def read_numbers_from_file(path):
	with open(path, 'r', encoding='utf-8') as f:
		text = f.read()
	# Extrae enteros (incluye negativos)
	nums = re.findall(r'-?\d+', text)
	return [int(n) for n in nums]


def main(input_path=None):
	if input_path is None:
		base = os.path.dirname(__file__)
		input_path = os.path.join(base, 'input.txt')

	if not os.path.exists(input_path):
		print(f'No existe el archivo de entrada: {input_path}', file=sys.stderr)
		return 1

	nums = read_numbers_from_file(input_path)
	if not nums:
		print('El archivo de entrada está vacío o no contiene números.', file=sys.stderr)
		return 1

	sorted_nums = quicksort(nums)
	print(' '.join(str(x) for x in sorted_nums))
	return 0


if __name__ == '__main__':
	path = None
	if len(sys.argv) > 1:
		path = sys.argv[1]
	raise SystemExit(main(path))
