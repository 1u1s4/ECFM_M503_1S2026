#!/usr/bin/env python3
"""
Lee un array desde `input.txt`, lo ordena usando quicksort y opcionalmente muestra trazas
de ejecución y la pila de llamadas.

Formato de `input.txt`: números enteros separados por espacios, comas o saltos de línea.
Ejemplo: [8 3 1 7 0 10 2 5]
"""
import argparse
import os
import re
import sys
from typing import List, Optional


class Tracer:
	def __init__(self, enabled: bool = False, show_stack: bool = False):
		self.enabled = enabled
		self.show_stack = show_stack
		self.stack = []  # lista de frames
		self.call_id = 0

	def _brief(self, arr: List[int], maxlen: int = 8) -> str:
		if len(arr) <= maxlen:
			return str(arr)
		return str(arr[:maxlen])[:-1] + f', ...] (len={len(arr)})'

	def enter(self, arr: List[int], pivot: int) -> int:
		self.call_id += 1
		frame = {'id': self.call_id, 'pivot': pivot, 'arr': list(arr)}
		self.stack.append(frame)
		if self.enabled:
			print(f"ENTER id={frame['id']} depth={len(self.stack)} pivot={pivot} arr={self._brief(arr)}")
			if self.show_stack:
				self._print_stack()
		return frame['id']

	def exit(self, call_id: int, result: List[int]):
		# pop until matching id (defensive)
		if not self.stack:
			return
		frame = self.stack.pop()
		if self.enabled:
			print(f"EXIT  id={call_id} depth={len(self.stack)+1} result={self._brief(result)}")
			if self.show_stack:
				self._print_stack()

	def _print_stack(self):
		stack_repr = ' -> '.join(f"id{f['id']}(len={len(f['arr'])})" for f in self.stack)
		print(f"STACK: {stack_repr}")


def quicksort(arr: List[int], tracer: Optional[Tracer] = None) -> List[int]:
	if len(arr) <= 1:
		return arr
	pivot = arr[len(arr) // 2]
	call_id = tracer.enter(arr, pivot) if tracer else None
	left = [x for x in arr if x < pivot]
	mid = [x for x in arr if x == pivot]
	right = [x for x in arr if x > pivot]
	sorted_left = quicksort(left, tracer)
	sorted_right = quicksort(right, tracer)
	result = sorted_left + mid + sorted_right
	if tracer:
		tracer.exit(call_id, result)
	return result


def read_numbers_from_file(path: str) -> List[int]:
	with open(path, 'r', encoding='utf-8') as f:
		text = f.read()
	# Extrae enteros (incluye negativos)
	nums = re.findall(r'-?\d+', text)
	return [int(n) for n in nums]


def parse_args():
	p = argparse.ArgumentParser(description='Quicksort con trazas opcionales desde input.txt')
	p.add_argument('--input', '-i', help='Ruta al archivo de entrada', default=None)
	p.add_argument('--trace', '-t', help='Mostrar trazas de llamadas', action='store_true')
	p.add_argument('--show-stack', '-s', help='Mostrar la pila de llamadas en cada traza', action='store_true')
	return p.parse_args()


def main(input_path: Optional[str] = None, trace: bool = False, show_stack: bool = False) -> int:
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

	tracer = Tracer(enabled=trace, show_stack=show_stack) if trace else None
	sorted_nums = quicksort(nums, tracer)
	print(' '.join(str(x) for x in sorted_nums))
	return 0


if __name__ == '__main__':
	args = parse_args()
	input_path = args.input
	raise SystemExit(main(input_path, trace=args.trace, show_stack=args.show_stack))
