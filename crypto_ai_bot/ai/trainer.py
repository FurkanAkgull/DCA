import os
import sys
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import yaml
import datetime

# Proje kök dizinini sys.path'e ekle ki 'analysis' ve diğer modüller bulunabilsin
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# logs ve models klasörlerini oluştur
os.makedirs(os.path.join(BASE_DIR, 'models'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

def train_model():
    # Konfigürasyonları YAML dosyasından oku
    config_path = os.path.join(BASE_DIR, 'config.yaml')
    with open(config_path) as f:
        config = yaml.safe_load(f)

    training_config = config['training']
    test_size = training_config.get('test_size', 0.2)
    n_estimators = training_config.get('rfc_n_estimators', 100)
    random_state = training_config.get('rfc_random_state', 42)

    data_path = os.path.join(BASE_DIR, 'data', 'historical_data.csv')
    model_path = os.path.join(BASE_DIR, 'models', 'rfc_model.pkl')

    df = pd.read_csv(data_path, index_col='timestamp', parse_dates=True)

    # Teknik göstergeleri ekle
    from analysis.indicators import add_indicators
    df = add_indicators(df)

    # Eksik verileri kaldır
    df.dropna(inplace=True)

    # Etiket: bir sonraki kapanış fiyatı şimdiki fiyattan yüksek mi?
    df['label'] = (df['close'].shift(-1) > df['close']).astype(int)

    df.dropna(inplace=True)

    X = df[['rsi', 'ema', 'macd']]
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, shuffle=False
    )

    # Modeli oluştur ve eğit
    model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
    model.fit(X_train, y_train)

    # Test doğruluğu hesapla
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model doğruluğu (accuracy): {acc:.2f}")

    # Eğitilen modeli dosyaya kaydet
    joblib.dump(model, model_path)
    print(f"Model kaydedildi: {model_path}")

    # Log dosyasına eğitim bilgilerini yaz
    log_path = os.path.join(BASE_DIR, 'logs', 'training.log')
    with open(log_path, 'a') as f:
        f.write(f"[{datetime.datetime.now()}] Accuracy: {acc:.4f}, Estimators: {n_estimators}\n")

if __name__ == "__main__":
    train_model()