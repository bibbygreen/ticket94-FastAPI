from enum import Enum

from pydantic import BaseModel


class AmegoTaxType(str, Enum):
    TAXABLE = "1"  # 應稅
    ZEROTAXRATE = "2"  # 零稅率
    TAXFREE = "3"  # 免稅
    SPECIALTAXRATE = "4"  # 應稅_特種稅率
    MIXED = "9"  # 混合應稅與免稅或零稅率


class ProductDetail(BaseModel):
    Description: str
    Quantity: str
    UnitPrice: str
    Amount: str
    TaxType: AmegoTaxType


class CreateAmegoInvoiceRequest(BaseModel):
    # https://invoice.amego.tw/api_doc/

    OrderId: str
    BuyerIdentifier: str | None = "0000000000"
    BuyerName: str | None = "0000000000"
    BuyerEmailAddress: str
    ProductItem: list[ProductDetail]
    SalesAmount: str
    FreeTaxSalesAmount: str
    ZeroTaxSalesAmount: str
    TaxType: AmegoTaxType
    TaxRate: str
    TaxAmount: str  # 營業稅額。有打統編才需計算5%稅額，沒打統編發票一律帶0。
    TotalAmount: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "OrderId": "A202008171059s34",
                    "BuyerIdentifier": "28080623",
                    "BuyerName": "光貿科技有限公司",
                    "BuyerEmailAddress": "0YsMl@example.com",
                    "ProductItem": [
                        {
                            "Description": "測試商品1",
                            "Quantity": "1",
                            "UnitPrice": "170",
                            "Amount": "170",
                            "TaxType": "1",
                        },
                        {
                            "Description": "會員折抵",
                            "Quantity": "1",
                            "UnitPrice": "-2",
                            "Amount": "-2",
                            "TaxType": "1",
                        },
                    ],
                    "SalesAmount": "160",
                    "FreeTaxSalesAmount": "0",
                    "ZeroTaxSalesAmount": "0",
                    "TaxType": "1",
                    "TaxRate": "0.05",
                    "TaxAmount": "8",
                    "TotalAmount": "168",
                }
            ]
        }
    }
