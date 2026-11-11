import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SWATCH_OUTPUT_PATH = os.path.join(BASE_DIR, 'results', 'visual_color_matching_swatches.png')

def rgb_to_norm(rgb):
    return np.clip(np.array(rgb) / 255.0, 0.0, 1.0)

def generate_swatches():
    # 3 Eksperimen Target
    experiments = [
        {
            'name': 'Target 1: Jingga / Oranye (M2 K3)',
            'target_rgb': (215, 140, 40),
            'initial_rgb': (245, 245, 245),
            'final_rgb': (164, 132, 43),
            'e_init': 142.65,
            'e_final': 29.67,
            'reduction': '79.2%',
            'drops': 'M=6, K=6, B=2 tetes',
            'note': 'Subtraktif: Dominan Kuning menyerap Blue & Merah menyerap Green'
        },
        {
            'name': 'Target 2: Hijau Botol (K3 B2)',
            'target_rgb': (65, 135, 75),
            'initial_rgb': (245, 245, 245),
            'final_rgb': (77, 96, 72),
            'e_init': 166.23,
            'e_final': 23.55,
            'reduction': '85.8%',
            'drops': 'M=4, K=4, B=9 tetes',
            'note': 'Subtraktif: Dominan Biru menyerap Red & Kuning menyerap Blue'
        },
        {
            'name': 'Target 3: Ungu Indigo (M3 B3)',
            'target_rgb': (120, 60, 110),
            'initial_rgb': (245, 245, 245),
            'final_rgb': (104, 86, 57),
            'e_init': 160.49,
            'e_final': 35.12,
            'reduction': '78.1%',
            'drops': 'M=10, K=4, B=5 tetes',
            'note': 'Subtraktif: Dominan Merah menyerap Green & Biru menyerap Red'
        }
    ]

    fig, axes = plt.subplots(3, 1, figsize=(13, 9.5))
    fig.patch.set_facecolor('#F8FAFC') # Soft executive background

    for idx, (exp, ax) in enumerate(zip(experiments, axes)):
        ax.set_facecolor('#FFFFFF')
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 3)
        ax.axis('off')

        # Outer card container border
        card = patches.FancyBboxPatch((0.1, 0.1), 11.8, 2.8, boxstyle="round,pad=0.1,rounding_size=0.2",
                                      edgecolor='#CBD5E1', facecolor='#FFFFFF', linewidth=1.2)
        ax.add_patch(card)

        # Title of target
        ax.text(0.4, 2.5, exp['name'], fontsize=13, fontweight='bold', color='#0F172A')
        ax.text(0.4, 2.2, f"Total Konsumsi Tetes: {exp['drops']}  |  {exp['note']}", fontsize=10, color='#64748B')

        # Box 1: Target Color
        c_tgt = rgb_to_norm(exp['target_rgb'])
        rect_tgt = patches.FancyBboxPatch((0.5, 0.4), 2.2, 1.5, boxstyle="round,pad=0.05,rounding_size=0.1",
                                          edgecolor='#0F172A', facecolor=c_tgt, linewidth=1.5)
        ax.add_patch(rect_tgt)
        ax.text(1.6, 1.25, 'TARGET ACUAN', fontsize=10, fontweight='bold', color='#FFFFFF' if np.mean(c_tgt) < 0.6 else '#000000', ha='center')
        ax.text(1.6, 0.7, f"RGB({exp['target_rgb'][0]}, {exp['target_rgb'][1]}, {exp['target_rgb'][2]})",
                fontsize=9, fontweight='bold', color='#FFFFFF' if np.mean(c_tgt) < 0.6 else '#000000', ha='center')

        # Arrow 1
        ax.annotate('', xy=(3.3, 1.15), xytext=(2.9, 1.15),
                    arrowprops=dict(facecolor='#94A3B8', edgecolor='#94A3B8', width=2, headwidth=7))

        # Box 2: Initial Water Color
        c_init = rgb_to_norm(exp['initial_rgb'])
        rect_init = patches.FancyBboxPatch((3.5, 0.4), 2.2, 1.5, boxstyle="round,pad=0.05,rounding_size=0.1",
                                           edgecolor='#CBD5E1', facecolor=c_init, linewidth=1.2)
        ax.add_patch(rect_init)
        ax.text(4.6, 1.25, 'AIR AWAL (Step 0)', fontsize=10, fontweight='bold', color='#334155', ha='center')
        ax.text(4.6, 0.9, f"RGB({exp['initial_rgb'][0]}, {exp['initial_rgb'][1]}, {exp['initial_rgb'][2]})",
                fontsize=9, color='#64748B', ha='center')
        ax.text(4.6, 0.6, f"Error E = {exp['e_init']:.1f}", fontsize=9, fontweight='bold', color='#DC2626', ha='center')

        # Arrow 2 (Fuzzy Control Action)
        ax.annotate('', xy=(6.5, 1.15), xytext=(5.9, 1.15),
                    arrowprops=dict(facecolor='#2563EB', edgecolor='#2563EB', width=3, headwidth=8))
        ax.text(6.2, 1.45, 'Kontrol Fuzzy\n+ Koreksi ANN', fontsize=8.5, fontweight='bold', color='#2563EB', ha='center')

        # Box 3: Final Achieved Color
        c_final = rgb_to_norm(exp['final_rgb'])
        rect_final = patches.FancyBboxPatch((6.7, 0.4), 2.2, 1.5, boxstyle="round,pad=0.05,rounding_size=0.1",
                                            edgecolor='#16A34A', facecolor=c_final, linewidth=2.0)
        ax.add_patch(rect_final)
        ax.text(7.8, 1.25, 'HASIL AKHIR', fontsize=10, fontweight='bold', color='#FFFFFF' if np.mean(c_final) < 0.6 else '#000000', ha='center')
        ax.text(7.8, 0.9, f"RGB({exp['final_rgb'][0]}, {exp['final_rgb'][1]}, {exp['final_rgb'][2]})",
                fontsize=9, fontweight='bold', color='#FFFFFF' if np.mean(c_final) < 0.6 else '#000000', ha='center')
        ax.text(7.8, 0.6, f"Error E = {exp['e_final']:.1f}", fontsize=9, fontweight='bold', color='#16A34A' if np.mean(c_final) < 0.6 else '#15803D', ha='center')

        # Stat Callout Badge on Right
        badge_box = patches.FancyBboxPatch((9.2, 0.4), 2.5, 1.5, boxstyle="round,pad=0.05,rounding_size=0.1",
                                           edgecolor='#86EFAC', facecolor='#F0FDF4', linewidth=1.2)
        ax.add_patch(badge_box)
        ax.text(10.45, 1.4, f"Reduksi Error: {exp['reduction']}", fontsize=11, fontweight='bold', color='#15803D', ha='center')
        ax.text(10.45, 1.0, f"Error Awal : {exp['e_init']:.1f}", fontsize=9, color='#475569', ha='center')
        ax.text(10.45, 0.7, f"Error Akhir: {exp['e_final']:.1f}", fontsize=9.5, fontweight='bold', color='#0F172A', ha='center')

    fig.suptitle('Validasi Visual Pencocokan Warna: Komparasi Swatch Closed-Loop Fuzzy Logic',
                 fontsize=15, fontweight='bold', color='#0F172A', y=0.98)
    plt.tight_layout()
    plt.savefig(SWATCH_OUTPUT_PATH, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Visual color swatch successfully saved to: {SWATCH_OUTPUT_PATH}")

if __name__ == '__main__':
    generate_swatches()
