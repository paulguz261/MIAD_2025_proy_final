# db/check_data.py
from sqlalchemy.orm import Session
from database import engine, Medicion

def revisar_datos():
    with Session(engine) as session:
        total = session.query(Medicion).count()
        print(f"Total de registros en la tabla 'mediciones': {total}")

        # Mostrar algunos ejemplos
        ejemplos = session.query(Medicion).limit(5).all()
        for m in ejemplos:
            print(f"[{m.fecha}] {m.cliente} - P: {m.presion}, T: {m.temperatura}, V: {m.volumen}")

def consulta_clientes():
    with Session(engine) as session:
        clientes = session.query(Medicion.cliente).distinct().all()
        print("Clientes únicos en la base de datos:")
        for cliente in clientes:
            print(cliente[0])

        page = 1
        limit = 3
        cliente = "CLIENTE1"
        offset = (page - 1) * limit
        query = session.query(Medicion).filter(Medicion.cliente.like(cliente))
        resultados = query.order_by(Medicion.fecha).offset(offset).limit(limit).all()
        # resultados = session.query(Medicion).filter(Medicion.cliente.ilike(cliente)).limit(5).all()
        print(resultados)
        print("→ Primer resultado:", resultados[0].__dict__)

if __name__ == "__main__":
    revisar_datos()
    consulta_clientes()