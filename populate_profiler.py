"""
populate_profiler.py
Popula o Atlas Performance Advisor e Query Profiler com queries variadas
sobre banco_inter (fatura + transacoes)
"""

import time
import random
from pymongo import MongoClient
from datetime import datetime

URI = "mongodb+srv://<user>:<password>@<cluster>.mongodb.net/banco_inter"

client = MongoClient(URI)
db = client["banco_inter"]
fatura = db["fatura"]
transacoes = db["transacoes"]

ACCOUNT_NUMBERS = [
    "2659850271393050232",
    "2375809432101401449",
    "2326393752287659295",
    "2287996907938235286",
    "2967547710284278035",
]

CATEGORY_CODES = ["5942", "5300", "5814", "5812", "5977", "5999", "5411", "5651"]
SEGMENTS      = ["s1", "s2", "s3", "s4"]
TX_TYPES      = ["d", "c"]
PLANS         = ["10002", "10003", "10006"]

total = 0

def run(label, cursor_or_result):
    global total
    try:
        if hasattr(cursor_or_result, 'to_list'):
            list(cursor_or_result)
        elif hasattr(cursor_or_result, '__iter__'):
            list(cursor_or_result)
        total += 1
        if total % 20 == 0:
            print(f"  [{total} queries] última: {label}")
    except Exception as e:
        print(f"  ERRO em {label}: {e}")

def batch(iteration):
    seg  = random.choice(SEGMENTS)
    cat  = random.choice(CATEGORY_CODES)
    acc  = random.choice(ACCOUNT_NUMBERS)
    typ  = random.choice(TX_TYPES)
    plan = random.choice(PLANS)
    amt_low  = str(random.randint(100, 2000))
    amt_high = str(random.randint(3000, 8000))

    # ── 1. Full scans simples ──────────────────────────────────────
    run("tx type", transacoes.find({"amos_mt_type": typ}).limit(100))
    run("fat type", fatura.find({"amss_mt_type": typ}).limit(100))

    # ── 2. Range por valor (sem índice regular) ────────────────────
    run("tx amount range", transacoes.find(
        {"amos_mt_amount": {"$gt": amt_low, "$lt": amt_high}}).limit(50))
    run("fat amount range", fatura.find(
        {"amss_mt_amount": {"$gt": amt_low, "$lt": amt_high}}).limit(50))

    # ── 3. Account + sort sem índice composto ─────────────────────
    run("tx account sort", transacoes.find(
        {"account_number": acc}).sort("amos_mt_amount", -1).limit(20))
    run("fat account sort", fatura.find(
        {"account_number": acc}).sort("amss_mt_amount", -1).limit(20))

    # ── 4. Categoria + segmento ───────────────────────────────────
    run("tx cat+seg", transacoes.find(
        {"amos_mt_category_code": cat, "segmento": seg}).limit(50))
    run("fat cat+seg", fatura.find(
        {"amss_mt_category_code": cat, "segmento": seg}).limit(50))

    # ── 5. Plano + tipo ───────────────────────────────────────────
    run("tx plan+type", transacoes.find(
        {"amos_mt_plan": plan, "amos_mt_type": typ}).limit(50))
    run("fat plan+type", fatura.find(
        {"amss_mt_plan": plan, "amss_mt_type": typ}).limit(50))

    # ── 6. Sort sem índice ────────────────────────────────────────
    run("tx sort amount desc", transacoes.find(
        {"segmento": seg}).sort("amos_mt_amount", -1).limit(30))
    run("fat sort amount desc", fatura.find(
        {"segmento": seg}).sort("amss_mt_amount", -1).limit(30))

    # ── 7. Aggregations ───────────────────────────────────────────
    run("tx agg cat total", transacoes.aggregate([
        {"$match": {"segmento": seg, "amos_mt_type": typ}},
        {"$group": {"_id": "$amos_mt_category_code",
                    "total": {"$sum": {"$toDouble": "$amos_mt_amount"}},
                    "count": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": 10}
    ]))

    run("fat agg cat total", fatura.aggregate([
        {"$match": {"segmento": seg, "amss_mt_type": typ}},
        {"$group": {"_id": "$amss_mt_category_code",
                    "total": {"$sum": {"$toDouble": "$amss_mt_amount"}},
                    "count": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": 10}
    ]))

    run("tx agg account profile", transacoes.aggregate([
        {"$match": {"account_number": acc}},
        {"$group": {"_id": "$amos_mt_category_code",
                    "total": {"$sum": {"$toDouble": "$amos_mt_amount"}},
                    "qtd":   {"$sum": 1},
                    "media": {"$avg": {"$toDouble": "$amos_mt_amount"}}}},
        {"$sort": {"total": -1}},
        {"$limit": 5}
    ]))

    run("tx agg top spenders", transacoes.aggregate([
        {"$match": {"segmento": seg}},
        {"$group": {"_id": "$account_number",
                    "total": {"$sum": {"$toDouble": "$amos_mt_amount"}}}},
        {"$sort": {"total": -1}},
        {"$limit": 10}
    ]))

    # ── 8. Date-like field filters ────────────────────────────────
    run("tx eff date", transacoes.find(
        {"amos_mt_eff_date": {"$gte": "20250101", "$lte": "20251231"}}).limit(50))
    run("fat eff date", fatura.find(
        {"amss_mt_eff_date": {"$gte": "20240101", "$lte": "20241231"}}).limit(50))

    # ── 9. Multi-field sem índice ─────────────────────────────────
    run("tx multi", transacoes.find({
        "segmento": seg,
        "amos_mt_type": typ,
        "amos_mt_plan": plan
    }).limit(30))

    run("fat multi", fatura.find({
        "segmento": seg,
        "amss_mt_type": typ,
        "amss_mt_plan": plan
    }).limit(30))

    # ── 10. installment queries ───────────────────────────────────
    inst = str(random.randint(1, 12))
    run("tx installment", transacoes.find(
        {"amos_mt_inst_nbr": inst, "segmento": seg}).limit(40))

    # ── 11. agg diaria ───────────────────────────────────────────
    run("tx agg diaria", transacoes.aggregate([
        {"$match": {"segmento": seg}},
        {"$group": {"_id": "$diaria_data",
                    "volume": {"$sum": {"$toDouble": "$amos_mt_amount"}},
                    "count":  {"$sum": 1}}},
        {"$sort": {"_id": -1}},
        {"$limit": 30}
    ]))

    # ── 12. Regex (muito lento, ótimo para Profiler) ──────────────
    prefixes = ["SHOPEE", "AMAZON", "IFOOD", "SUPERMERCADO", "FORT"]
    prefix = random.choice(prefixes)
    run("tx regex desc", transacoes.find(
        {"amos_mt_desc": {"$regex": f"^{prefix}", "$options": "i"}}).limit(20))
    run("fat regex desc", fatura.find(
        {"amss_mt_desc": {"$regex": f"^{prefix}", "$options": "i"}}).limit(20))


# ── MAIN ──────────────────────────────────────────────────────────────
ROUNDS = 10
print(f"Iniciando {ROUNDS} rodadas de queries...")
print(f"Início: {datetime.now().strftime('%H:%M:%S')}\n")

for i in range(1, ROUNDS + 1):
    print(f"Rodada {i}/{ROUNDS}...")
    batch(i)
    time.sleep(0.5)

print(f"\nFinalizado: {datetime.now().strftime('%H:%M:%S')}")
print(f"Total de queries executadas: {total}")
print("\nAcesse no Atlas UI:")
print("  → Performance Advisor: sugestões de índices")
print("  → Profiler: todas as queries com tempo e plano de execução")

client.close()
