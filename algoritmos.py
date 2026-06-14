import heapq
from collections import Counter


# ─────────────────────────────────────────
#  HUFFMAN
# ─────────────────────────────────────────
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman(text):
    """Construye el árbol de Huffman. Retorna (raiz, Counter de frecuencias)."""
    freq = Counter(text)
    if len(freq) == 1:
        char = next(iter(freq))
        root = Node(char, freq[char])
        return root, freq
    heap = [Node(char, f) for char, f in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)
    return heap[0], freq


def get_huffman_codes(node, current_code="", codes=None):
    """Recorre el árbol en DFS y asigna un código binario a cada símbolo."""
    if codes is None:
        codes = {}
    if node is None:
        return codes
    if node.char is not None:
        codes[node.char] = current_code if current_code else "0"
    get_huffman_codes(node.left,  current_code + "0", codes)
    get_huffman_codes(node.right, current_code + "1", codes)
    return codes


def huffman_encode(text, codes):
    return "".join(codes[c] for c in text)


def huffman_decode(encoded, root):
    if root is None:
        return ""
    # Caso símbolo único
    if root.left is None and root.right is None:
        return root.char * len(encoded)
    decoded = []
    current = root
    for bit in encoded:
        current = current.left if bit == "0" else current.right
        if current.char is not None:
            decoded.append(current.char)
            current = root
    return "".join(decoded)


# ─────────────────────────────────────────
#  SHANNON-FANO
# ─────────────────────────────────────────
def shannon_fano(symbols_freq, codes=None, prefix=""):
    """
    Partición recursiva de Shannon-Fano.
    symbols_freq: lista de (símbolo, frecuencia) ordenada descendente.
    """
    if codes is None:
        codes = {}
    if not symbols_freq:
        return codes
    if len(symbols_freq) == 1:
        codes[symbols_freq[0][0]] = prefix if prefix else "0"
        return codes
    total = sum(f for _, f in symbols_freq)
    acc, min_diff, split_idx = 0, float("inf"), 0
    for i, (_, f) in enumerate(symbols_freq):
        acc += f
        diff = abs((total - acc) - acc)
        if diff < min_diff:
            min_diff = diff
            split_idx = i
    shannon_fano(symbols_freq[: split_idx + 1], codes, prefix + "0")
    shannon_fano(symbols_freq[split_idx + 1 :],  codes, prefix + "1")
    return codes


def sf_encode(text, codes):
    return "".join(codes[c] for c in text)


def sf_decode(encoded, codes):
    reverse = {v: k for k, v in codes.items()}
    decoded, temp = [], ""
    for bit in encoded:
        temp += bit
        if temp in reverse:
            decoded.append(reverse[temp])
            temp = ""
    return "".join(decoded)
