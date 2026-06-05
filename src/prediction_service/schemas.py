"""在线预测服务的请求/响应数据契约（Pydantic v2）。

入参为 19 个客户特征（已剔除泄漏字段 duration）。
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Customer(BaseModel):
    """单个客户的 19 个特征。"""

    # 类别字段
    job: str = Field(..., description="职业，如 admin.")
    marital: str = Field(..., description="婚姻状况")
    education: str = Field(..., description="教育水平")
    default: str = Field(..., description="是否有违约记录 yes/no")
    housing: str = Field(..., description="是否有房贷 yes/no")
    loan: str = Field(..., description="是否有个人贷款 yes/no")
    contact: str = Field(..., description="联系方式，如 cellular")
    month: str = Field(..., description="最后联系月份，如 aug")
    day_of_week: str = Field(..., description="最后联系星期，如 mon")
    poutcome: str = Field(..., description="上次营销结果")

    # 数值字段
    age: float = Field(..., description="年龄")
    campaign: float = Field(..., description="本次活动联系次数")
    pdays: float = Field(..., description="距上次联系天数")
    previous: float = Field(..., description="之前联系次数")
    emp_var_rate: float = Field(..., description="就业变动率")
    cons_price_index: float = Field(..., description="消费者物价指数")
    cons_conf_index: float = Field(..., description="消费者信心指数")
    lending_rate3m: float = Field(..., description="3 月期利率")
    nr_employed: float = Field(..., description="在职人数")

    model_config = {
        "json_schema_extra": {
            "example": {
                "job": "admin.",
                "marital": "married",
                "education": "university.degree",
                "default": "no",
                "housing": "yes",
                "loan": "no",
                "contact": "cellular",
                "month": "may",
                "day_of_week": "mon",
                "poutcome": "nonexistent",
                "age": 41,
                "campaign": 2,
                "pdays": 999,
                "previous": 0,
                "emp_var_rate": -1.8,
                "cons_price_index": 92.89,
                "cons_conf_index": -46.2,
                "lending_rate3m": 1.31,
                "nr_employed": 5099.1,
            }
        }
    }


class PredictionResult(BaseModel):
    """单条预测结果。"""

    subscribe: str = Field(..., description="预测是否认购 yes/no")
    probability: float = Field(..., description="认购概率(0~1)")
    confidence: str = Field(..., description="置信度 high/medium/low")


class BatchRequest(BaseModel):
    """批量预测请求。"""

    customers: list[Customer]


class BatchResponse(BaseModel):
    """批量预测响应。"""

    results: list[PredictionResult]
