import math
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np


def calculate_metrics(text, codes, freqs):
    """
    Calcula métricas de compresión.
    Retorna: (bits_orig, bits_comp, tasa_%, longitud_media, entropía, eficiencia_%)
    """
    total = len(text)
    original_bits = total * 8
    compressed_bits = sum(freqs[c] * len(codes[c]) for c in freqs)
    tasa = (compressed_bits / original_bits) * 100 if original_bits else 0
    avg_length = compressed_bits / total if total else 0
    entropy = -sum((f / total) * math.log2(f / total) for f in freqs.values() if f > 0)
    # K=2 (alfabeto binario); eficiencia = H / (L * log2(K)) = H / L
    efficiency = (entropy / avg_length) * 100 if avg_length > 0 else 0
    return original_bits, compressed_bits, tasa, avg_length, entropy, efficiency


def build_symbol_rows(freqs, codes, total):
    """
    Retorna lista de dicts con info por símbolo, ordenada por frecuencia desc.
    Cada dict: {char, freq, prob, code, length}
    """
    rows = []
    for char, freq in sorted(freqs.items(), key=lambda x: x[1], reverse=True):
        rows.append({
            "char":   char,
            "freq":   freq,
            "prob":   freq / total,
            "code":   codes.get(char, ""),
            "length": len(codes.get(char, "")),
        })
    return rows


def show_charts(freqs, h_codes, s_codes, plot_data):
    """
    Muestra dos figuras:
      Fig 1 – Tabla visual de símbolos (Huffman y Shannon-Fano lado a lado)
      Fig 2 – Gráficos de barras: métricas globales + frecuencia vs longitudes
    """
    total = sum(freqs.values())
    symbols_sorted = sorted(freqs.items(), key=lambda x: x[1], reverse=True)
    top = symbols_sorted[:14]   # máx 14 para legibilidad
    labels = [repr(s) for s, _ in top]

    freq_vals = [freqs[s]        for s, _ in top]
    h_len     = [len(h_codes[s]) for s, _ in top]
    s_len     = [len(s_codes[s]) for s, _ in top]

    x = np.arange(len(labels))
    w = 0.28

    # ── FIGURA 1: Tabla de símbolos ──────────────────────────────────────────
    fig1, axes = plt.subplots(1, 2, figsize=(13, max(4, len(freqs) * 0.45 + 1.5)))
    fig1.suptitle("Tabla de Símbolos y Códigos", fontsize=13, fontweight="bold", y=1.01)

    for ax, name, codes in [(axes[0], "Huffman", h_codes), (axes[1], "Shannon-Fano", s_codes)]:
        rows = build_symbol_rows(freqs, codes, total)
        col_labels = ["Símbolo", "Freq", "Prob", "Código", "Long."]
        cell_data = [
            [repr(r["char"]), str(r["freq"]), f'{r["prob"]:.4f}', r["code"], str(r["length"])]
            for r in rows
        ]
        ax.axis("off")
        tbl = ax.table(
            cellText=cell_data,
            colLabels=col_labels,
            loc="center",
            cellLoc="center",
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(9)
        tbl.scale(1, 1.4)
        # Cabecera en color
        for col in range(len(col_labels)):
            tbl[0, col].set_facecolor("#2c3e50")
            tbl[0, col].set_text_props(color="white", fontweight="bold")
        # Filas alternas
        for row in range(1, len(rows) + 1):
            color = "#eaf2fb" if row % 2 == 0 else "white"
            for col in range(len(col_labels)):
                tbl[row, col].set_facecolor(color)
        ax.set_title(name, fontsize=11, fontweight="bold", pad=8)

    plt.tight_layout()

    # ── FIGURA 2: Gráficos de barras ─────────────────────────────────────────
    fig2 = plt.figure(figsize=(14, 10))
    fig2.suptitle("Análisis de Compresión — Huffman vs Shannon-Fano",
                  fontsize=13, fontweight="bold")
    gs = gridspec.GridSpec(2, 2, figure=fig2, hspace=0.45, wspace=0.35)

    # ── Subplot 1: Métricas globales ──
    ax1 = fig2.add_subplot(gs[0, 0])
    m_labels = ["Tasa\nComp (%)", "Eficiencia\n(%)", "Long.\nPromedio (bits)", "Entropía\n(bits/símbolo)"]
    h_vals = [plot_data["h_rate"], plot_data["h_eff"], plot_data["h_avg"], plot_data["h_ent"]]
    s_vals = [plot_data["s_rate"], plot_data["s_eff"], plot_data["s_avg"], plot_data["s_ent"]]
    xm = np.arange(len(m_labels))
    b1 = ax1.bar(xm - 0.2, h_vals, 0.38, label="Huffman",      color="#2980b9")
    b2 = ax1.bar(xm + 0.2, s_vals, 0.38, label="Shannon-Fano", color="#e67e22")
    ax1.set_xticks(xm); ax1.set_xticklabels(m_labels, fontsize=8)
    ax1.set_title("Métricas Globales", fontweight="bold")
    ax1.legend(fontsize=8)
    for bar in list(b1) + list(b2):
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, h + 0.3, f"{h:.1f}",
                 ha="center", va="bottom", fontsize=7)

    # ── Subplot 2: Frecuencia de símbolos ──
    ax2 = fig2.add_subplot(gs[0, 1])
    ax2.bar(x, freq_vals, color="#27ae60", alpha=0.85)
    ax2.set_xticks(x); ax2.set_xticklabels(labels, rotation=40, ha="right", fontsize=8)
    ax2.set_title(f"Frecuencia de Símbolos (top {len(top)})", fontweight="bold")
    ax2.set_ylabel("Frecuencia")

    # ── Subplot 3: Longitud de código por símbolo ──
    ax3 = fig2.add_subplot(gs[1, :])
    ax3.bar(x - w, freq_vals, w, label="Frecuencia",      color="#27ae60", alpha=0.75)
    ax3.bar(x,     h_len,     w, label="Long. Huffman",   color="#2980b9", alpha=0.9)
    ax3.bar(x + w, s_len,     w, label="Long. Shannon-F", color="#e67e22", alpha=0.9)
    ax3.set_xticks(x); ax3.set_xticklabels(labels, rotation=40, ha="right", fontsize=8)
    ax3.set_title(f"Frecuencia vs Longitud de Código (top {len(top)} símbolos)", fontweight="bold")
    ax3.set_ylabel("Valor")
    ax3.legend(fontsize=9)

    plt.tight_layout()
    plt.show()
