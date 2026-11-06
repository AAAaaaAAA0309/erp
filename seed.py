from app.database import SessionLocal, Base, engine
from app.models import User, Warehouse, Product, Partner
from app.auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if not db.query(User).first():
    db.add(User(username="admin", hashed_password=hash_password("admin123"), role="admin"))
    db.add(User(username="manager", hashed_password=hash_password("manager123"), role="manager"))

if not db.query(Warehouse).first():
    w1 = Warehouse(name="Основной", address="Москва, ул. Складская, 1")
    w2 = Warehouse(name="Ромашка", address="Москва, ул. Ромашковая, 5")
    db.add_all([w1, w2]); db.commit()
    db.add_all([
        Product(name="Гвоздь 50мм", sku="GV-50", unit="шт", stock=120, warehouse_id=w1.id),
        Product(name="Гвоздь 100мм", sku="GV-100", unit="шт", stock=80, warehouse_id=w1.id),
        Product(name="Шуруп 3х20", sku="SH-320", unit="шт", stock=350, warehouse_id=w2.id),
        Product(name="Молоток 500г", sku="ML-500", unit="шт", stock=15, warehouse_id=w2.id),
    ])
    db.add_all([
        Partner(name="ООО Ромашка", inn="7701234567", type="customer"),
        Partner(name="ИП Иванов", inn="770987654321", type="supplier"),
    ])

db.commit()
print("Seed OK. Логины: admin/admin123, manager/manager123")