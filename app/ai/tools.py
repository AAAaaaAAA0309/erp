import json
from sqlalchemy.orm import Session
from ..models import Product, Partner, Warehouse

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_stock",
            "description": "Вернуть остатки товаров. Фильтры опциональны. Если пользователь спрашивает про конкретный товар или склад, передай product_name и/или warehouse_name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "Часть названия товара"},
                    "warehouse_name": {"type": "string", "description": "Название склада"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_partners",
            "description": "Вернуть список контрагентов (до 50).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_partner",
            "description": "Создать нового контрагента. ВСЕГДА сначала вызывай с confirmed=False, чтобы показать черновик. Если пользователь подтвердил, вызывай снова с confirmed=True.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Полное название"},
                    "inn": {"type": "string"},
                    "type": {"type": "string", "enum": ["customer", "supplier"]},
                    "confirmed": {"type": "boolean", "description": "Поставь True, только если пользователь явно подтвердил создание."}
                },
                "required": ["name", "confirmed"],
            },
        },
    },
]

def execute_tool(name: str, args: dict, db: Session, user) -> dict:
    try:
        if name == "get_stock":
            q = db.query(Product)
            if args.get("product_name"):
                q = q.filter(Product.name.ilike(f"%{args['product_name']}%"))
            if args.get("warehouse_name"):
                q = q.join(Warehouse).filter(Warehouse.name.ilike(f"%{args['warehouse_name']}%"))
            items = q.limit(50).all()
            return {"count": len(items), "items": [
                {"name": p.name, "sku": p.sku, "stock": p.stock, "unit": p.unit,
                 "warehouse": p.warehouse.name if p.warehouse else None}
                for p in items
            ]}

        if name == "list_partners":
            items = db.query(Partner).limit(50).all()
            return {"count": len(items), "items": [
                {"name": p.name, "inn": p.inn, "type": p.type} for p in items
            ]}

        if name == "create_partner":
            # Если ИИ не получил подтверждения, мы возвращаем ему "черновик"
            if not args.get("confirmed"):
                return {
                    "status": "needs_confirmation",
                    "message": f"Вы уверены, что хотите создать контрагента '{args['name']}' (ИНН: {args.get('inn', 'нет')}, Тип: {args.get('type', 'customer')})? Напишите 'Да' для подтверждения."
                }
            
            # Если confirmed=True, создаем в базе
            if user.role != "admin" and user.role != "manager":
                return {"error": "Недостаточно прав"}
            p = Partner(name=args["name"], inn=args.get("inn", ""), type=args.get("type", "customer"))
            db.add(p); db.commit(); db.refresh(p)
            return {"ok": True, "message": f"Успех! Контрагент {p.name} создан."}

        return {"error": f"Неизвестный инструмент: {name}"}
    except Exception as e:
        return {"error": str(e)}