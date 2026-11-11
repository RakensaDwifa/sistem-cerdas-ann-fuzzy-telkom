import csv
import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt

# Kunci seed untuk keterulangan hasil (reproducibility)
torch.manual_seed(42)
np.random.seed(42)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATASET_PATH = os.path.join(BASE_DIR, 'data', 'dataset_sistem_cerdas_90.csv')
MODEL_SAVE_PATH = os.path.join(BASE_DIR, 'models', 'model_ann_koreksi_terbaik.pt')
PLOT_SAVE_PATH = os.path.join(BASE_DIR, 'results', 'grafik_loss_pelatihan_ann.png')
EVAL_CSV_PATH = os.path.join(BASE_DIR, 'data', 'evaluasi_model_ann_mae.csv')
PRED_CSV_PATH = os.path.join(BASE_DIR, 'data', 'prediksi_data_uji_ann.csv')

# 1. Membaca Dataset
train_data, test_data = [], []
with open(DATASET_PATH, 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        item = {
            'mixture': row['mixture'],
            'condition': row['condition'],
            'filename': row['filename'],
            'X': [float(row[k]) for k in ['Rs', 'Gs', 'Bs', 'Rref', 'Gref', 'Bref']],
            'Y': [float(row[k]) for k in ['Rt', 'Gt', 'Bt']],
            'split': row['split']
        }
        if row['split'] == 'Train':
            train_data.append(item)
        else:
            test_data.append(item)

print(f"Data Latih: {len(train_data)} sampel (dari 24 campuran)")
print(f"Data Uji Unseen: {len(test_data)} sampel (dari 6 campuran)")

# Konversi ke PyTorch Tensor dan Normalisasi [0, 1]
X_train = torch.tensor([d['X'] for d in train_data], dtype=torch.float32) / 255.0
Y_train = torch.tensor([d['Y'] for d in train_data], dtype=torch.float32) / 255.0

X_test = torch.tensor([d['X'] for d in test_data], dtype=torch.float32) / 255.0
Y_test = torch.tensor([d['Y'] for d in test_data], dtype=torch.float32) / 255.0

raw_test_rgb = torch.tensor([[d['X'][0], d['X'][1], d['X'][2]] for d in test_data], dtype=torch.float32)
target_test_rgb = torch.tensor([d['Y'] for d in test_data], dtype=torch.float32)

# Evaluasi Awal: Error Sebelum Koreksi pada Data Uji
mae_before_R = torch.mean(torch.abs(raw_test_rgb[:, 0] - target_test_rgb[:, 0])).item()
mae_before_G = torch.mean(torch.abs(raw_test_rgb[:, 1] - target_test_rgb[:, 1])).item()
mae_before_B = torch.mean(torch.abs(raw_test_rgb[:, 2] - target_test_rgb[:, 2])).item()
mae_before_tot = (mae_before_R + mae_before_G + mae_before_B) / 3.0

# 2. Definisi Arsitektur ANN (Sesuai TOR: Minimal 2 Konfigurasi)
class ANN_1Layer(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(6, 16),
            nn.ReLU(),
            nn.Linear(16, 3)
        )
    def forward(self, x):
        return self.net(x)

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

def train_model(model, epochs=1500, lr=0.005):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    train_history = []
    test_history = []
    
    for ep in range(epochs):
        model.train()
        optimizer.zero_grad()
        out = model(X_train)
        loss = criterion(out, Y_train)
        loss.backward()
        optimizer.step()
        train_history.append(loss.item())
        
        with torch.no_grad():
            t_loss = criterion(model(X_test), Y_test).item()
            test_history.append(t_loss)
            
    model.eval()
    with torch.no_grad():
        preds_rgb = model(X_test) * 255.0
        mae_R = torch.mean(torch.abs(preds_rgb[:, 0] - target_test_rgb[:, 0])).item()
        mae_G = torch.mean(torch.abs(preds_rgb[:, 1] - target_test_rgb[:, 1])).item()
        mae_B = torch.mean(torch.abs(preds_rgb[:, 2] - target_test_rgb[:, 2])).item()
        mae_tot = (mae_R + mae_G + mae_B) / 3.0
        
    return model, train_history, test_history, (mae_R, mae_G, mae_B, mae_tot), preds_rgb

print("\nMelatih Model 1 (1 Hidden Layer: 16)...")
m1, tr_l1, te_l1, mae_m1, p_m1 = train_model(ANN_1Layer())

print("Melatih Model 2 (2 Hidden Layer: 32-16)...")
m2, tr_l2, te_l2, mae_m2, p_m2 = train_model(ANN_2Layer())

# 3. Simpan Bobot Model Terbaik (Model 2)
torch.save({
    'model_state_dict': m2.state_dict(),
    'architecture': 'ANN_2Layer (6 -> 32 -> 16 -> 3)',
    'input_scale': 255.0,
    'output_scale': 255.0,
    'mae_test': mae_m2
}, MODEL_SAVE_PATH)
print(f"Model terbaik tersimpan di: {MODEL_SAVE_PATH}")

# 4. Simpan Tabel Evaluasi MAE
with open(EVAL_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Konfigurasi', 'MAE R', 'MAE G', 'MAE B', 'Mean MAE', 'Penurunan Error (%)'])
    w.writerow(['Sebelum Koreksi (Baseline)', f'{mae_before_R:.2f}', f'{mae_before_G:.2f}', f'{mae_before_B:.2f}', f'{mae_before_tot:.2f}', '0.0%'])
    pct1 = ((mae_before_tot - mae_m1[3]) / mae_before_tot) * 100
    w.writerow(['Model 1 (1 Hidden Layer: 16)', f'{mae_m1[0]:.2f}', f'{mae_m1[1]:.2f}', f'{mae_m1[2]:.2f}', f'{mae_m1[3]:.2f}', f'{pct1:.1f}%'])
    pct2 = ((mae_before_tot - mae_m2[3]) / mae_before_tot) * 100
    w.writerow(['Model 2 (2 Hidden Layer: 32-16)', f'{mae_m2[0]:.2f}', f'{mae_m2[1]:.2f}', f'{mae_m2[2]:.2f}', f'{mae_m2[3]:.2f}', f'{pct2:.1f}%'])

# 5. Simpan Rincian Prediksi Data Uji
with open(PRED_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Mixture', 'Condition', 'Rs_raw', 'Gs_raw', 'Bs_raw', 'Rc_pred', 'Gc_pred', 'Bc_pred', 'Rt_target', 'Gt_target', 'Bt_target', 'Error_Sebelum', 'Error_Sesudah'])
    for i, item in enumerate(test_data):
        err_before = np.sqrt(np.mean([(raw_test_rgb[i][k].item() - target_test_rgb[i][k].item())**2 for k in range(3)]))
        err_after = np.sqrt(np.mean([(p_m2[i][k].item() - target_test_rgb[i][k].item())**2 for k in range(3)]))
        w.writerow([
            item['mixture'], item['condition'],
            f'{raw_test_rgb[i][0].item():.1f}', f'{raw_test_rgb[i][1].item():.1f}', f'{raw_test_rgb[i][2].item():.1f}',
            f'{p_m2[i][0].item():.1f}', f'{p_m2[i][1].item():.1f}', f'{p_m2[i][2].item():.1f}',
            f'{target_test_rgb[i][0].item():.1f}', f'{target_test_rgb[i][1].item():.1f}', f'{target_test_rgb[i][2].item():.1f}',
            f'{err_before:.2f}', f'{err_after:.2f}'
        ])

# 6. Gambar Kurva Loss Pelatihan
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

ax1.plot(tr_l1, label='Train Loss', color='blue')
ax1.plot(te_l1, label='Test Loss (Unseen)', color='orange', linestyle='--')
ax1.set_title('Model 1 (1 Hidden Layer: 16)')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('MSE Loss')
ax1.set_ylim(0, 0.05)
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.legend()

ax2.plot(tr_l2, label='Train Loss', color='green')
ax2.plot(te_l2, label='Test Loss (Unseen)', color='red', linestyle='--')
ax2.set_title('Model 2 (2 Hidden Layer: 32-16)')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('MSE Loss')
ax2.set_ylim(0, 0.05)
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.legend()

plt.tight_layout()
plt.savefig(PLOT_SAVE_PATH, dpi=300)
plt.close()
print(f"Grafik kurva loss tersimpan di: {PLOT_SAVE_PATH}")
