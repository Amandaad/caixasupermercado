from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import Annotated

Username = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=80)]
Barcode = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]
ProductName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=180)]

class LoginInput(BaseModel):
    username: Username
    password: str = Field(min_length=1, max_length=200)

class TokenOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProductCreate(BaseModel):
    barcode: Barcode
    name: ProductName
    category_id: int | None = None
    unit: str = Field(default="UN", min_length=1, max_length=12)
    cost_price: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=12, decimal_places=2)
    sale_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    stock_qty: Decimal = Field(default=Decimal("0.000"), ge=0, max_digits=12, decimal_places=3)
    min_stock: Decimal = Field(default=Decimal("0.000"), ge=0, max_digits=12, decimal_places=3)

class ProductUpdate(BaseModel):
    barcode: Barcode | None = None
    name: ProductName | None = None
    category_id: int | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=12)
    cost_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    sale_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    min_stock: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=3)
    active: bool | None = None

class ProductOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    barcode: str
    name: str
    category_id: int | None
    unit: str
    cost_price: Decimal
    sale_price: Decimal
    stock_qty: Decimal
    min_stock: Decimal
    active: bool
