import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

def create_fuzzy_color_controller():
    # 1. Definisi Universe of Discourse
    # Error: [-120, 120]
    eR = ctrl.Antecedent(np.arange(-120, 121, 1), 'eR')
    eG = ctrl.Antecedent(np.arange(-120, 121, 1), 'eG')
    eB = ctrl.Antecedent(np.arange(-120, 121, 1), 'eB')

    # Output: Tetes [0, 5]
    dM = ctrl.Consequent(np.arange(0, 5.1, 0.1), 'dM', defuzzify_method='centroid')
    dK = ctrl.Consequent(np.arange(0, 5.1, 0.1), 'dK', defuzzify_method='centroid')
    dB = ctrl.Consequent(np.arange(0, 5.1, 0.1), 'dB', defuzzify_method='centroid')

    # 2. Fungsi Keanggotaan (Membership Functions)
    # Error: LN (Large Negative), SN (Small Negative), Z (Zero), P (Positive)
    for err in [eR, eG, eB]:
        err['LN'] = fuzz.trapmf(err.universe, [-120, -120, -50, -20])
        err['SN'] = fuzz.trimf(err.universe, [-40, -20, 0])
        err['Z']  = fuzz.trimf(err.universe, [-15, 0, 15])
        err['P']  = fuzz.trapmf(err.universe, [0, 20, 120, 120])

    # Output: Z (Zero), S (Small), M (Medium), L (Large)
    for out in [dM, dK, dB]:
        out['Z'] = fuzz.trimf(out.universe, [0.0, 0.0, 0.5])
        out['S'] = fuzz.trimf(out.universe, [0.2, 1.0, 2.0])
        out['M'] = fuzz.trimf(out.universe, [1.5, 2.5, 3.5])
        out['L'] = fuzz.trapmf(out.universe, [3.0, 4.0, 5.0, 5.0])

    # 3. Basis Aturan Fuzzy (Subtractive Dye Chemistry)
    # Larutan berwarna terbentuk dengan menyerap spektrum cahaya tertentu:
    # - Merah (M) ditambahkan jika kanal G perlu ditekan lebih banyak dibanding R (eG < eR)
    # - Kuning (K) ditambahkan jika kanal B perlu ditekan lebih banyak dibanding G (eB < eG)
    # - Biru (B) ditambahkan jika kanal R perlu ditekan lebih banyak dibanding G & B (eR < eG atau eR < eB)

    rules = [
        # --- Aturan Tetes Merah (M): Menyerap Green ---
        ctrl.Rule(eG['LN'] & ~eR['LN'], dM['L']),
        ctrl.Rule(eG['SN'] & ~eR['LN'], dM['S']),
        ctrl.Rule(eG['LN'] & eR['LN'], dM['M']),
        ctrl.Rule(eG['Z'] | eG['P'], dM['Z']),

        # --- Aturan Tetes Kuning (K): Menyerap Blue ---
        ctrl.Rule(eB['LN'] & ~eG['LN'], dK['L']),
        ctrl.Rule(eB['SN'] & ~eG['LN'], dK['S']),
        ctrl.Rule(eB['LN'] & eG['LN'], dK['M']),
        ctrl.Rule(eB['Z'] | eB['P'], dK['Z']),

        # --- Aturan Tetes Biru (B): Menyerap Red ---
        ctrl.Rule(eR['LN'] & ~eB['LN'], dB['L']),
        ctrl.Rule(eR['SN'] & ~eB['LN'], dB['S']),
        ctrl.Rule(eR['LN'] & eB['LN'], dB['M']),
        ctrl.Rule(eR['Z'] | eR['P'], dB['Z']),

        # --- Prioritas & Pencegahan Kontaminasi Warna ---
        # Jika Target Oranye (eB sangat minus tapi eR tidak se-minus eB): Dilarang tambah Biru
        ctrl.Rule(eB['LN'] & eG['SN'], dB['Z']),
        # Jika Target Hijau (eR sangat minus tapi eG tidak se-minus eR): Dilarang tambah Merah
        ctrl.Rule(eR['LN'] & eB['LN'] & (eG['SN'] | eG['Z']), dM['Z']),
        # Jika Target Ungu (eG sangat minus tapi eB tidak se-minus eG): Dilarang tambah Kuning
        ctrl.Rule(eG['LN'] & (eB['SN'] | eB['Z']), dK['Z']),

        # Kondisi Seimbang / On Target
        ctrl.Rule((eR['Z'] | eR['P']) & (eG['Z'] | eG['P']) & (eB['Z'] | eB['P']), (dM['Z'], dK['Z'], dB['Z']))
    ]

    control_system = ctrl.ControlSystem(rules)
    sim = ctrl.ControlSystemSimulation(control_system)
    return sim, (eR, eG, eB), (dM, dK, dB)

def compute_fuzzy_drops(sim, eR_val, eG_val, eB_val):
    sim.input['eR'] = np.clip(eR_val, -120, 120)
    sim.input['eG'] = np.clip(eG_val, -120, 120)
    sim.input['eB'] = np.clip(eB_val, -120, 120)
    sim.compute()

    dM_raw = sim.output['dM']
    dK_raw = sim.output['dK']
    dB_raw = sim.output['dB']

    # Konversi ke tetes diskrit integer (pembulatan dengan batas minimal 0 dan maksimal 5)
    dM_int = int(np.round(dM_raw))
    dK_int = int(np.round(dK_raw))
    dB_int = int(np.round(dB_raw))

    return (dM_raw, dK_raw, dB_raw), (dM_int, dK_int, dB_int)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
def plot_membership_functions(save_path=None):
    if save_path is None:
        save_path = os.path.join(BASE_DIR, 'results', 'grafik_fungsi_keanggotaan_fuzzy.png')
    _, (eR, eG, eB), (dM, dK, dB) = create_fuzzy_color_controller()
    
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    
    # Input Error MFs
    for term in ['LN', 'SN', 'Z', 'P']:
        axes[0, 0].plot(eR.universe, eR[term].mf, label=term, linewidth=2)
    axes[0, 0].set_title('Fungsi Keanggotaan Input Error (eR, eG, eB)', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Error RGB (e = Target - Current)')
    axes[0, 0].set_ylabel('Derajat Keanggotaan (μ)')
    axes[0, 0].grid(True, linestyle=':', alpha=0.6)
    axes[0, 0].legend()

    # Output MFs for dM
    for term in ['Z', 'S', 'M', 'L']:
        axes[0, 1].plot(dM.universe, dM[term].mf, label=term, linewidth=2)
    axes[0, 1].set_title('Fungsi Keanggotaan Output Tetes Merah (dM)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Volume Tetes Merah (drops)')
    axes[0, 1].set_ylabel('Derajat Keanggotaan (μ)')
    axes[0, 1].grid(True, linestyle=':', alpha=0.6)
    axes[0, 1].legend()

    # Output MFs for dK
    for term in ['Z', 'S', 'M', 'L']:
        axes[1, 0].plot(dK.universe, dK[term].mf, label=term, linewidth=2)
    axes[1, 0].set_title('Fungsi Keanggotaan Output Tetes Kuning (dK)', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Volume Tetes Kuning (drops)')
    axes[1, 0].set_ylabel('Derajat Keanggotaan (μ)')
    axes[1, 0].grid(True, linestyle=':', alpha=0.6)
    axes[1, 0].legend()

    # Output MFs for dB
    for term in ['Z', 'S', 'M', 'L']:
        axes[1, 1].plot(dB.universe, dB[term].mf, label=term, linewidth=2)
    axes[1, 1].set_title('Fungsi Keanggotaan Output Tetes Biru (dB)', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Volume Tetes Biru (drops)')
    axes[1, 1].set_ylabel('Derajat Keanggotaan (μ)')
    axes[1, 1].grid(True, linestyle=':', alpha=0.6)
    axes[1, 1].legend()

    plt.suptitle('Desain Kontroler Fuzzy Logic Mamdani Pencocokan Warna (CPMK-3)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Fuzzy membership plots saved to: {save_path}")

if __name__ == '__main__':
    plot_membership_functions()
    sim, _, _ = create_fuzzy_color_controller()
    
    # Test cases
    test_errors = [
        (-60, -10, 0),   # Butuh kurangi R drastis -> Blue dye
        (0, -70, -10),   # Butuh kurangi G drastis -> Red dye
        (0, 0, -80),     # Butuh kurangi B drastis -> Yellow dye
        (0, 0, 0),       # On target -> All 0
        (30, 20, 10),    # Over-saturated -> All 0
    ]
    print("\n--- TEST KONTROLER FUZZY ---")
    for er, eg, eb in test_errors:
        raw, discrete = compute_fuzzy_drops(sim, er, eg, eb)
        print(f"Error ({er:3d}, {eg:3d}, {eb:3d}) -> Raw drops: M={raw[0]:.2f}, K={raw[1]:.2f}, B={raw[2]:.2f} => Diskrit: M={discrete[0]}, K={discrete[1]}, B={discrete[2]}")
