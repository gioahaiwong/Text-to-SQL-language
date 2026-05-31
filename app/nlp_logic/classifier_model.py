import torch
import torch.nn as nn
from transformers import AutoModel, AutoConfig

class MyClassifier(nn.Module):
    def __init__(
        self,
        model_name_or_path,
        vocab_size,
        mode
    ):
        super(MyClassifier, self).__init__()
        config = AutoConfig.from_pretrained(model_name_or_path)
        self.plm_encoder = AutoModel.from_config(config)
        self.plm_encoder.resize_token_embeddings(vocab_size)
        
        hidden_size = config.hidden_size
        
        # Table Classification Head (Matching keys in dense_classifier.pt)
        self.table_name_bilstm = nn.LSTM(
            input_size=hidden_size,
            hidden_size=hidden_size // 2,
            num_layers=2,
            batch_first=True,
            bidirectional=True
        )
        self.table_name_linear_after_pooling = nn.Linear(hidden_size, hidden_size)
        self.table_name_cls_head_linear1 = nn.Linear(hidden_size, 256)
        self.table_name_cls_head_linear2 = nn.Linear(256, 2)
        
        # Column Classification Head (Matching keys in dense_classifier.pt)
        self.column_info_bilstm = nn.LSTM(
            input_size=hidden_size,
            hidden_size=hidden_size // 2,
            num_layers=2,
            batch_first=True,
            bidirectional=True
        )
        self.column_info_linear_after_pooling = nn.Linear(hidden_size, hidden_size)
        self.column_info_cls_head_linear1 = nn.Linear(hidden_size, 256)
        self.column_info_cls_head_linear2 = nn.Linear(256, 2)
        
        # Cross Attention
        self.table_column_cross_attention_layer = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=8,
            batch_first=True
        )
        
        self.dropout = nn.Dropout(0.1)

    def forward(self, *args, **kwargs):
        # We only use this for ranking if we enable filtering
        pass
