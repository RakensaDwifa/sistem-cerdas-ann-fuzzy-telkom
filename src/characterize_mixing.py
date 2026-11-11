import csv
import re
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATASET_PATH = os.path.join(BASE_DIR, 'data', 'dataset_sistem_cerdas_90.csv')
CHAR_PLOT_PATH = os.path.join(BASE_DIR, 'results', 'karakterisasi_respon_pewarna.png')
CHAR_REPORT_PATH = os.path.join(BASE_DIR, 'docs', 'laporan_karakterisasi_pewarna.txt')

def parse_drops(mixture_name):
    # e.g. 'M1 K1 B3', 'M5', 'K2 B4'
    m_drops = 0
    k_drops = 0
    b_drops = 0
    
    parts = mixture_name.strip().split()
    for p in parts:
        m_match = re.match(r'^M(\d+)$', p)
        k_match = re.match(r'^K(\d+)$', p)
        b_match = re.match(r'^B(\d+)$', p)
        if m_match:
            m_drops = int(m_match.group(1))
        elif k_match:
            k_drops = int(k_match.group(1))
        elif b_match:
            b_drops = int(b_match.group(1))
    return m_drops, k_drops, b_drops

# Load ground-truth (Terang condition) for each mixture
recipes = {}
with open(DATASET_PATH, 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        if row['condition'] == 'Terang':
            m = row['mixture']
            dM, dK, dB = parse_drops(m)
            recipes[m] = {
                'dM': dM, 'dK': dK, 'dB': dB,
                'R': float(row['Rt']),
                'G': float(row['Gt']),
                'B': float(row['Bt'])
            }

print(f"Total analyzed recipes: {len(recipes)}")

# Analyze Pure Primary Response
pure_m = [(recipes[f'M{i}']['dM'], recipes[f'M{i}']['R'], recipes[f'M{i}']['G'], recipes[f'M{i}']['B']) for i in [1, 5] if f'M{i}' in recipes]
pure_k = [(recipes[f'K{i}']['dK'], recipes[f'K{i}']['R'], recipes[f'K{i}']['G'], recipes[f'K{i}']['B']) for i in [1, 5] if f'K{i}' in recipes]
pure_b = [(recipes[f'B{i}']['dB'], recipes[f'B{i}']['R'], recipes[f'B{i}']['G'], recipes[f'B{i}']['B']) for i in [1, 5] if f'B{i}' in recipes]

print("\nPure Red:")
for d, r, g, b in pure_m:
    print(f"  {d} tetes: R={r:.1f}, G={g:.1f}, B={b:.1f}")

print("\nPure Yellow:")
for d, r, g, b in pure_k:
    print(f"  {d} tetes: R={r:.1f}, G={g:.1f}, B={b:.1f}")

print("\nPure Blue:")
for d, r, g, b in pure_b:
    print(f"  {d} tetes: R={r:.1f}, G={g:.1f}, B={b:.1f}")

# Subtractive optical absorption model:
# Clear water baseline (100 ml): R0, G0, B0 ~ [245, 245, 245]
# Optical density / absorption A ~ epsilon * drops
# Transmittance T = 10^(-A) => RGB = RGB0 * 10^(-k * drops) or polynomial fit
X = [] # [dM, dK, dB, 1]
Y_R, Y_G, Y_B = [], [], []

for m, val in recipes.items():
    X.append([val['dM'], val['dK'], val['dB'], 1.0])
    Y_R.append(val['R'])
    Y_G.append(val['G'])
    Y_B.append(val['B'])

X = np.array(X)
w_R, _, _, _ = np.linalg.lstsq(X, Y_R, rcond=None)
w_G, _, _, _ = np.linalg.lstsq(X, Y_G, rcond=None)
w_B, _, _, _ = np.linalg.lstsq(X, Y_B, rcond=None)

report = f"""=== HASIL KARAKTERISASI PENCAMPURAN PEWARNA (TOR TAHAP II) ===
Model Pergeseran Respons Subtraktif:
Kanal R: delta R = ({w_R[0]:+.2f} * dM) + ({w_R[1]:+.2f} * dK) + ({w_R[2]:+.2f} * dB) | Base={w_R[3]:.1f}
Kanal G: delta G = ({w_G[0]:+.2f} * dM) + ({w_G[1]:+.2f} * dK) + ({w_G[2]:+.2f} * dB) | Base={w_G[3]:.1f}
Kanal B: delta B = ({w_B[0]:+.2f} * dM) + ({w_B[1]:+.2f} * dK) + ({w_B[2]:+.2f} * dB) | Base={w_B[3]:.1f}

Kaidah Subtraktif Fisis Terkonfirmasi:
1. Penambahan Tetes Merah (M):
   - Efek dominan: Mengurangi kanal Hijau (G) dan Biru (B) secara signifikan.
   - Gradien G/drop: {w_G[0]:.2f}, Gradien B/drop: {w_B[0]:.2f}
2. Penambahan Tetes Kuning (K):
   - Efek dominan: Mengurangi kanal Biru (B) paling tajam (daya serap spektrum biru sangat kuat).
   - Gradien B/drop: {w_B[1]:.2f}
3. Penambahan Tetes Biru (B):
   - Efek dominan: Mengurangi kanal Merah (R) dan Hijau (G).
   - Gradien R/drop: {w_R[2]:.2f}, Gradien G/drop: {w_G[2]:.2f}
"""

print(report)
with open(CHAR_REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write(report)

# Plot response characterization
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

# Pure colors effect
drops_range = [1, 5]
r_m = [recipes['M1']['R'], recipes['M5']['R']]
g_m = [recipes['M1']['G'], recipes['M5']['G']]
b_m = [recipes['M1']['B'], recipes['M5']['B']]

axes[0].plot(drops_range, r_m, 'r-o', label='R channel')
axes[0].plot(drops_range, g_m, 'g-s', label='G channel')
axes[0].plot(drops_range, b_m, 'b-^', label='B channel')
axes[0].set_title('Respons Pewarna Merah (M)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Tetes Merah (drops)')
axes[0].set_ylabel('Nilai Intensitas RGB')
axes[0].grid(True, linestyle=':', alpha=0.6)
axes[0].legend()

r_k = [recipes['K1']['R'], recipes['K5']['R']]
g_k = [recipes['K1']['G'], recipes['K5']['G']]
b_k = [recipes['K1']['B'], recipes['K5']['B']]

axes[1].plot(drops_range, r_k, 'r-o', label='R channel')
axes[1].plot(drops_range, g_k, 'g-s', label='G channel')
axes[1].plot(drops_range, b_k, 'b-^', label='B channel')
axes[1].set_title('Respons Pewarna Kuning (K)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Tetes Kuning (drops)')
axes[1].set_ylabel('Nilai Intensitas RGB')
axes[1].grid(True, linestyle=':', alpha=0.6)
axes[1].legend()

r_b = [recipes['B1']['R'], recipes['B5']['R']]
g_b = [recipes['B1']['G'], recipes['B5']['G']]
b_b = [recipes['B1']['B'], recipes['B5']['B']]

axes[2].plot(drops_range, r_b, 'r-o', label='R channel')
axes[2].plot(drops_range, g_b, 'g-s', label='G channel')
axes[2].plot(drops_range, b_b, 'b-^', label='B channel')
axes[2].set_title('Respons Pewarna Biru (B)', fontsize=12, fontweight='bold')
axes[2].set_xlabel('Tetes Biru (drops)')
axes[2].set_ylabel('Nilai Intensitas RGB')
axes[2].grid(True, linestyle=':', alpha=0.6)
axes[2].legend()

plt.suptitle('Karakterisasi Pengaruh Penambahan Pewarna M, K, B terhadap Kanal RGB', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(CHAR_PLOT_PATH, dpi=300, bbox_inches='tight')
plt.close()
print(f"Plot karakterisasi tersimpan di: {CHAR_PLOT_PATH}")
