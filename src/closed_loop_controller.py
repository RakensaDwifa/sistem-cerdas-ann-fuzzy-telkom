import os
import sys
import argparse
import csv
import cv2
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from fuzzy_controller import create_fuzzy_color_controller, compute_fuzzy_drops

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODEL_PT_PATH = os.path.join(BASE_DIR, 'models', 'model_ann_koreksi_terbaik.pt')
SIM_LOG_CSV = os.path.join(BASE_DIR, 'data', 'log_simulasi_closed_loop_fuzzy.csv')
CONVERGENCE_PLOT_PATH = os.path.join(BASE_DIR, 'results', 'grafik_konvergensi_closed_loop.png')

# 1. Definisi Arsitektur Model ANN PyTorch
class ANN_2Layer(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(6, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 3)
        )
    def forward(self, x):
        return self.net(x)

def load_trained_ann():
    model = ANN_2Layer()
    checkpoint = torch.load(MODEL_PT_PATH, weights_only=True)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    return model

def predict_corrected_rgb(model, sample_rgb, ref_rgb):
    """
    Prediksi RGB terkoreksi Rc, Gc, Bc menggunakan PyTorch ANN Model 2
    Input: sample_rgb [Rs, Gs, Bs], ref_rgb [Rref, Gref, Bref] skala 0-255
    Output: corrected_rgb [Rc, Gc, Bc] skala 0-255
    """
    x_input = list(sample_rgb) + list(ref_rgb)
    x_tensor = torch.tensor([x_input], dtype=torch.float32) / 255.0
    with torch.no_grad():
        y_pred = model(x_tensor) * 255.0
    return np.clip(y_pred.numpy()[0], 0.0, 255.0)

def extract_roi_from_image(image_path):
    """
    Mengekstrak rata-rata spasial ROI Sampel Cairan & ROI Kartu Abu-Abu
    Sesuai koordinat baku proyek:
    ROI Sampel Cairan: Y=[430:510], X=[600:680]
    ROI Kartu Abu-Abu: Y=[450:550], X=[200:300]
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Gagal membaca citra dari: {image_path}")
    
    # Konversi BGR (OpenCV) ke RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Ekstraksi ROI
    roi_sample = img_rgb[430:510, 600:680]
    roi_ref = img_rgb[450:550, 200:300]
    
    sample_mean = np.mean(roi_sample, axis=(0, 1))
    ref_mean = np.mean(roi_ref, axis=(0, 1))
    
    return sample_mean, ref_mean

def simulate_optical_absorption(current_rgb, dM, dK, dB):
    """
    Simulator fisis absorpsi optik subtraktif berbasis karakteristik spektral:
    - Merah (M) menyerap spektrum Hijau (G) & Biru (B)
    - Kuning (K) menyerap spektrum Biru (B)
    - Biru (B) menyerap spektrum Merah (R) & Hijau (G)
    """
    # Koefisien reduksi intensitas cahaya per tetes (hukum Bouguer-Lambert empiris)
    # R_new = R * exp(-alpha_R * drops), G_new = G * exp(-alpha_G * drops), etc.
    k_M = np.array([0.02, 0.08, 0.06]) # dM menyerap G & B kuat
    k_K = np.array([0.01, 0.01, 0.25]) # dK menyerap B sangat kuat
    k_B = np.array([0.15, 0.09, 0.02]) # dB menyerap R & G kuat

    total_k = (k_M * dM) + (k_K * dK) + (k_B * dB)
    transmittance = np.exp(-total_k)
    new_rgb = current_rgb * transmittance
    return np.clip(new_rgb, 0.0, 255.0)

def run_closed_loop_simulation():
    print("=================================================================")
    print("  SIMULASI CLOSED-LOOP FUZZY LOGIC COLOR MATCHING (TOR TAHAP II) ")
    print("=================================================================")
    
    ann_model = load_trained_ann()
    fuzzy_sim, _, _ = create_fuzzy_color_controller()

    # 3 Target Warna yang mewakili spektrum campuran biner dan tersier
    targets = [
        {
            'name': 'Target 1: Jingga / Oranye (M2 K3)',
            'target_rgb': np.array([215.0, 140.0, 40.0]),
            'ref_rgb': np.array([205.0, 208.0, 142.0]) # Referensi pencahayaan acuan
        },
        {
            'name': 'Target 2: Hijau Botol (K3 B2)',
            'target_rgb': np.array([65.0, 135.0, 75.0]),
            'ref_rgb': np.array([205.0, 208.0, 142.0])
        },
        {
            'name': 'Target 3: Ungu Indigo (M3 B3)',
            'target_rgb': np.array([120.0, 60.0, 110.0]),
            'ref_rgb': np.array([205.0, 208.0, 142.0])
        }
    ]

    all_logs = []
    plot_data = {}

    for t_idx, target in enumerate(targets):
        t_name = target['name']
        t_rgb = target['target_rgb']
        ref_rgb = target['ref_rgb']
        print(f"\n>>> Memulai Uji Kontrol: {t_name}")
        print(f"    Target RGB : [R={t_rgb[0]:.1f}, G={t_rgb[1]:.1f}, B={t_rgb[2]:.1f}]")

        # Kondisi awal: air bersih 100 ml (larutan bening awal di wadah ~ RGB 240, 240, 240)
        curr_sample_rgb = np.array([245.0, 245.0, 245.0])
        cum_drops = {'M': 0, 'K': 0, 'B': 0}
        history_E_rgb = []

        for step in range(1, 7): # Maksimal 6 langkah sesuai batas kontrol TOR
            # 1. Koreksi ANN Model 2
            corrected_rgb = predict_corrected_rgb(ann_model, curr_sample_rgb, ref_rgb)

            # 2. Hitung Error kanal RGB sesuai rumus TOR
            eR = t_rgb[0] - corrected_rgb[0]
            eG = t_rgb[1] - corrected_rgb[1]
            eB = t_rgb[2] - corrected_rgb[2]

            # 3. Hitung Indikator Error E_RGB sesuai TOR Bagian 11
            E_rgb = np.sqrt((eR**2 + eG**2 + eB**2) / 3.0)
            history_E_rgb.append(E_rgb)

            print(f"  Step {step}:")
            print(f"    Terukur (ANN Corrected): [R={corrected_rgb[0]:.1f}, G={corrected_rgb[1]:.1f}, B={corrected_rgb[2]:.1f}]")
            print(f"    Error: [eR={eR:+.1f}, eG={eG:+.1f}, eB={eB:+.1f}] | E_RGB = {E_rgb:.2f}")

            # Kriteria berhenti (Toleransi tercapai E_RGB <= 15.0)
            if E_rgb <= 15.0:
                print(f"    [SUKSES] Toleransi warna tercapai pada langkah ke-{step}! (E_RGB <= 15.0)")
                all_logs.append({
                    'Target': t_name, 'Step': step, 'Status': 'CONVERGED',
                    'Rc': corrected_rgb[0], 'Gc': corrected_rgb[1], 'Bc': corrected_rgb[2],
                    'eR': eR, 'eG': eG, 'eB': eB, 'E_RGB': E_rgb,
                    'Add_M': 0, 'Add_K': 0, 'Add_B': 0,
                    'Tot_M': cum_drops['M'], 'Tot_K': cum_drops['K'], 'Tot_B': cum_drops['B']
                })
                break

            # 4. Inferensi Fuzzy Mamdani
            _, (dM_int, dK_int, dB_int) = compute_fuzzy_drops(fuzzy_sim, eR, eG, eB)
            print(f"    Keputusan Fuzzy -> Tambah: M={dM_int} tetes, K={dK_int} tetes, B={dB_int} tetes")

            # Catat log
            all_logs.append({
                'Target': t_name, 'Step': step, 'Status': 'IN_PROGRESS',
                'Rc': corrected_rgb[0], 'Gc': corrected_rgb[1], 'Bc': corrected_rgb[2],
                'eR': eR, 'eG': eG, 'eB': eB, 'E_RGB': E_rgb,
                'Add_M': dM_int, 'Add_K': dK_int, 'Add_B': dB_int,
                'Tot_M': cum_drops['M'] + dM_int, 'Tot_K': cum_drops['K'] + dK_int, 'Tot_B': cum_drops['B'] + dB_int
            })

            # Jika Fuzzy tidak merekomendasikan tetesan tambahan lagi (stuck)
            if dM_int == 0 and dK_int == 0 and dB_int == 0:
                print("    [STOP] Tidak ada penambahan tetes lebih lanjut yang direkomendasikan.")
                break

            # Update akumulasi tetes
            cum_drops['M'] += dM_int
            cum_drops['K'] += dK_int
            cum_drops['B'] += dB_int

            # 5. Simulasi respons perubahan optik cairan
            curr_sample_rgb = simulate_optical_absorption(curr_sample_rgb, dM_int, dK_int, dB_int)

        plot_data[t_name] = history_E_rgb

    # 6. Simpan Log CSV
    with open(SIM_LOG_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Target', 'Step', 'Status', 'Rc', 'Gc', 'Bc', 'eR', 'eG', 'eB', 'E_RGB', 'Add_M', 'Add_K', 'Add_B', 'Tot_M', 'Tot_K', 'Tot_B']
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_logs:
            w.writerow(r)
    print(f"\nLog eksperimen closed-loop tersimpan di: {SIM_LOG_CSV}")

    # 7. Gambar Grafik Konvergensi Error
    plt.figure(figsize=(9, 5.5))
    colors = ['#E65100', '#2E7D32', '#6A1B9A']
    markers = ['o', 's', '^']

    for (t_name, errs), col, m in zip(plot_data.items(), colors, markers):
        steps = list(range(1, len(errs) + 1))
        label_clean = t_name.split(':')[1].strip()
        plt.plot(steps, errs, marker=m, color=col, linewidth=2.2, markersize=7, label=label_clean)

    plt.axhline(y=15.0, color='red', linestyle='--', linewidth=1.5, label='Batas Toleransi Target (E_RGB = 15)')
    plt.title('Dinamika Konvergensi Kontroler Fuzzy Logic Closed-Loop', fontsize=13, fontweight='bold')
    plt.xlabel('Langkah Pencampuran (Step)', fontsize=11)
    plt.ylabel('Error Euclidean RGB (E_RGB)', fontsize=11)
    plt.xticks(range(1, 7))
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend(fontsize=10.5)
    plt.tight_layout()
    plt.savefig(CONVERGENCE_PLOT_PATH, dpi=300)
    plt.close()
    print(f"Grafik konvergensi error tersimpan di: {CONVERGENCE_PLOT_PATH}")

def run_interactive_mode():
    print("=================================================================")
    print("  MODE INTERAKTIF CLOSED-LOOP FUZZY LOGIC (LABORATORIUM FISIK)   ")
    print("=================================================================")
    ann_model = load_trained_ann()
    fuzzy_sim, _, _ = create_fuzzy_color_controller()

    print("\nMasukkan Target Warna yang Ingin Dicapai:")
    try:
        r_t = float(input("  Target Red   (0-255): "))
        g_t = float(input("  Target Green (0-255): "))
        b_t = float(input("  Target Blue  (0-255): "))
    except ValueError:
        print("Input tidak valid. Menggunakan target default Oranye (215, 140, 40).")
        r_t, g_t, b_t = 215.0, 140.0, 40.0

    target_rgb = np.array([r_t, g_t, b_t])
    print(f"\nTarget Terpilih: [R={target_rgb[0]}, G={target_rgb[1]}, B={target_rgb[2]}]")
    print("Persiapkan wadah berisi 100 ml air bersih dan letakkan kartu abu-abu netral 18% di samping wadah.")

    cum_drops = {'M': 0, 'K': 0, 'B': 0}

    for step in range(1, 7):
        print(f"\n--- LANGKAH {step} / 6 ---")
        img_path = input("Masukkan path file foto larutan saat ini (atau 'q' untuk keluar): ").strip('\"\'')
        if img_path.lower() == 'q':
            break

        if not os.path.exists(img_path):
            print(f"File '{img_path}' tidak ditemukan. Coba lagi.")
            continue

        sample_rgb, ref_rgb = extract_roi_from_image(img_path)
        print(f"  Ekstraksi ROI Berhasil:")
        print(f"    Sample Raw: [R={sample_rgb[0]:.1f}, G={sample_rgb[1]:.1f}, B={sample_rgb[2]:.1f}]")
        print(f"    Ref Card  : [R={ref_rgb[0]:.1f}, G={ref_rgb[1]:.1f}, B={ref_rgb[2]:.1f}]")

        # Koreksi ANN
        corrected_rgb = predict_corrected_rgb(ann_model, sample_rgb, ref_rgb)
        eR = target_rgb[0] - corrected_rgb[0]
        eG = target_rgb[1] - corrected_rgb[1]
        eB = target_rgb[2] - corrected_rgb[2]
        E_rgb = np.sqrt((eR**2 + eG**2 + eB**2) / 3.0)

        print(f"  Hasil Koreksi ANN Model 2:")
        print(f"    Corrected RGB: [R={corrected_rgb[0]:.1f}, G={corrected_rgb[1]:.1f}, B={corrected_rgb[2]:.1f}]")
        print(f"    Error Kanal  : [eR={eR:+.1f}, eG={eG:+.1f}, eB={eB:+.1f}]")
        print(f"    Toleransi E_RGB: {E_rgb:.2f}")

        if E_rgb <= 15.0:
            print(f"\n[SUKSES!] Toleransi target tercapai pada langkah ke-{step} (E_RGB <= 15.0)!")
            break

        _, (dM, dK, dB) = compute_fuzzy_drops(fuzzy_sim, eR, eG, eB)
        cum_drops['M'] += dM
        cum_drops['K'] += dK
        cum_drops['B'] += dB

        print(f"\n>>> REKOMENDASI TETES DARI KONTROLER FUZZY:")
        print(f"    + Teteskan Merah (M)  : {dM} tetes")
        print(f"    + Teteskan Kuning (K) : {dK} tetes")
        print(f"    + Teteskan Biru (B)   : {dB} tetes")
        print(f"    Total Akumulasi Tetes : M={cum_drops['M']}, K={cum_drops['K']}, B={cum_drops['B']}")
        print("Silakan teteskan pewarna, aduk perlahan 5 detik hingga homogen, lalu ambil foto baru.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Closed-Loop Fuzzy Logic Color Matching")
    parser.add_argument('--mode', choices=['simulate', 'interactive'], default='simulate',
                        help="Pilih mode eksekusi: 'simulate' untuk uji komputasi cepat, 'interactive' untuk lab fisik")
    args = parser.parse_args()

    if args.mode == 'simulate':
        run_closed_loop_simulation()
    else:
        run_interactive_mode()
