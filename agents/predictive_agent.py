import torch
import torch.nn as nn
import numpy as np
from state import PortfolioState

class SimplePriceLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=16, num_layers=1):
        super(SimplePriceLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

def predictive_agent(state: PortfolioState) -> PortfolioState:
    if state.get("error") or not state.get("price_data"):
        return {}

    closes = state["price_data"]["close"]
    if len(closes) < 10:
        return {"dl_prediction": "Veri Yetersiz"}

    recent_data = np.array(closes[-10:])
    min_val, max_val = np.min(recent_data), np.max(recent_data)
    if max_val > min_val:
        scaled_data = (recent_data - min_val) / (max_val - min_val)
    else:
        scaled_data = recent_data

    input_tensor = torch.tensor(scaled_data, dtype=torch.float32).unsqueeze(0).unsqueeze(-1)
    model = SimplePriceLSTM()
    model.eval()

    with torch.no_grad():
        prediction = model(input_tensor).item()

    last_scaled_val = scaled_data[-1]
    if prediction > last_scaled_val:
        trend = "YÜKSELİŞ BEKLENTİSİ"
    else:
        trend = "DÜŞÜŞ BEKLENTİSİ"

    return {"dl_prediction": trend}