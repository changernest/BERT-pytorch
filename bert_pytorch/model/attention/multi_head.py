import torch.nn as nn
from .single import Attention


class MultiHeadedAttention(nn.Module):
    """
    Take in model size and number of heads.
    """

    def __init__(self, h, d_model, dropout=0.1):
        super().__init__()
        assert d_model % h == 0

        # We assume d_v always equals d_k, 每个小头的维度
        self.d_k = d_model // h
        # 头的个数
        self.h = h

        # k,v,q对应的三个w变化矩阵
        self.linear_layers = nn.ModuleList([nn.Linear(d_model, d_model) for _ in range(3)])

        self.output_linear = nn.Linear(d_model, d_model)
        self.attention = Attention()

        self.dropout = nn.Dropout(p=dropout)

    def forward(self, query, key, value, mask=None):
        # query [batch_size, seq_len, d_model]
        batch_size = query.size(0)

        # query [batch_size, head_size, seq_len, d_k]
        # 1) Do all the linear projections in batch from d_model => h x d_k
        query, key, value = [l(x).view(batch_size, -1, self.h, self.d_k).transpose(1, 2)
                             for l, x in zip(self.linear_layers, (query, key, value))]

        # query [batch_size, head_size, seq_len, d_k]
        # 2) Apply attention on all the projected vectors in batch.
        x, attn = self.attention(query, key, value, mask=mask, dropout=self.dropout)

        # [batch_size, seq_len，d_model]
        # 3) "Concat" using a view and apply a final linear.
        x = x.transpose(1, 2).contiguous().view(batch_size, -1, self.h * self.d_k)

        # [batch_size, seq_len，d_model]
        return self.output_linear(x)
