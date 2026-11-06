from pydantic import BaseModel, ConfigDict

class ProductBase(BaseModel):
    name: str
    sku: str
    unit: str = "шт"
    stock: int = 0
    warehouse_id: int | None = None

class ProductCreate(ProductBase): pass
class ProductOut(ProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class WarehouseBase(BaseModel):
    name: str
    address: str = ""

class WarehouseCreate(WarehouseBase): pass
class WarehouseOut(WarehouseBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class PartnerBase(BaseModel):
    name: str
    inn: str = ""
    address: str = ""
    type: str = "customer"

class PartnerCreate(PartnerBase): pass
class PartnerOut(PartnerBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    actions: list[dict] = []