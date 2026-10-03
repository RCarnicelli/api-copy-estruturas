from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import hmac
from search_engine import buscar_swipes
from swipe_queries import listar_categorias_postgres, carregar_swipes_postgres, cards_para_categoria, SwipeReadError
import psycopg
from init_db import init_database
from crawler import capturar_pagina, normalizar_pagina, descobrir_links_swipefile, validar_pagina_swipefile
from classifier import classificar_swipe
from swipe_repository import salvar_swipe
from ingestion import processar_lote, IngestionBusy, validar_lote
from semantic import backfill_embeddings, buscar_swipes_semanticos, SemanticError
app = Flask(__name__)
CORS(app)


@app.errorhandler(SemanticError)
def semantic_error(error):
    return jsonify({"erro": str(error)}), 503


@app.route('/embeddings', methods=['POST'])
def embeddings_endpoint():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"erro": "Informe um objeto JSON"}), 400
    dry_run = body.get('dry_run', True)
    if dry_run is not True:
        token = os.environ.get('SWIPE_EMBEDDING_TOKEN', '')
        provided = request.headers.get('Authorization', '')
        if len(token) < 32 or not hmac.compare_digest(provided.encode(), ('Bearer ' + token).encode()):
            return jsonify({"erro": "Autenticação de vetorização necessária"}), 401
    try:
        return jsonify(backfill_embeddings(body.get('limite', 25), dry_run))
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400

    except Exception:
        return jsonify({"erro": "Falha ao executar vetorização"}), 503


@app.route('/taxonomy/apply', methods=['POST'])
def taxonomy_apply_endpoint():
    # Explicit dev opt-in prevents accidental activation on another service.
    if os.environ.get('SWIPE_TAXONOMY_ENABLED') != '1':
        return jsonify({'erro': 'Migração de taxonomia desativada'}), 503
    token = os.environ.get('SWIPE_EMBEDDING_TOKEN', '')
    provided = request.headers.get('Authorization', '')
    if len(token) < 32 or not hmac.compare_digest(provided.encode(), ('Bearer ' + token).encode()):
        return jsonify({'erro': 'Autenticação administrativa necessária'}), 401
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or not isinstance(body.get('dry_run', True), bool):
        return jsonify({'erro': 'Informe dry_run booleano'}), 400
    try:
        from taxonomy import apply_curated_taxonomy
        dry_run = body.get('dry_run', True)
        if not dry_run:
            init_database()
        return jsonify(apply_curated_taxonomy(dry_run))
    except ValueError as error:
        return jsonify({'erro': str(error)}), 409
    except Exception:
        return jsonify({'erro': 'Falha ao aplicar taxonomia'}), 503


@app.route('/buscar-swipes-semanticos', methods=['POST'])
def semantic_search_endpoint():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"erro": "Informe um objeto JSON"}), 400
    try:
        return jsonify(buscar_swipes_semanticos(body.get('consulta'), body.get('categoria'),
                       body.get('objetivo'), body.get('emocao'), body.get('tom'), body.get('limite', 5)))
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400


@app.errorhandler(SwipeReadError)
def postgres_read_error(error):
    return jsonify({"erro": "PostgreSQL indisponível para consulta"}), 503


def _autorizar_ingestao():
    token = os.environ.get("SWIPE_INGESTION_TOKEN", "")
    if os.environ.get("SWIPE_INGESTION_ENABLED") != "1" or len(token) < 32:
        return jsonify({"erro": "Ingestão paga desativada"}), 503
    provided = request.headers.get("Authorization", "")
    if not hmac.compare_digest(provided.encode("utf-8"), ("Bearer " + token).encode("utf-8")):
        return jsonify({"erro": "Autenticação de ingestão necessária"}), 401
    return None


@app.route('/processar-swipes', methods=['POST'])
def processar_swipes_endpoint():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"erro": "Informe um objeto JSON"}), 400
    urls, limite, dry_run = body.get("urls"), body.get("limite", 1), body.get("dry_run", True)
    try:
        validar_lote(urls, limite, dry_run)
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400
    if not dry_run:
        denied = _autorizar_ingestao()
        if denied is not None:
            return denied
    try:
        return jsonify(processar_lote(urls, limite, dry_run))
    except IngestionBusy:
        return jsonify({"erro": "Já existe uma ingestão em andamento"}), 409
    except Exception:
        return jsonify({"erro": "Falha ao executar o lote"}), 500
@app.route('/init-db', methods=['GET'])
def init_db():
    try:
        init_database()
        return jsonify({
            "status": "ok",
            "message": "Banco inicializado e migrado"
        })
    except Exception as e:
        return jsonify({
            "status": "erro",
            "detalhe": str(e)
        }), 500
@app.route('/')
def home():
    return "API de swipes está no ar!"

@app.route('/test-crawler', methods=['GET'])
def test_crawler():
    url = request.args.get("url")

    if not url:
        return jsonify({"erro": "URL não informada"}), 400
    denied = _autorizar_ingestao()
    if denied is not None:
        return denied
    try:
        result = processar_lote([url], limite=1, dry_run=False)
        if result["resultados"]:
            result["id_salvo"] = result["resultados"][0].get("id")
        return jsonify(result)
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400
    except IngestionBusy:
        return jsonify({"erro": "Já existe uma ingestão em andamento"}), 409
    except Exception:
        return jsonify({"erro": "Falha ao processar o swipe"}), 500
@app.route('/coletar-swipes', methods=['GET'])
def coletar_swipes():
    url = request.args.get(
        "url",
        "https://swipefile.com/database"
    )

    try:
        url = validar_pagina_swipefile(url)
        resultado = capturar_pagina(url)
        links = descobrir_links_swipefile(resultado, base_url=url)

        return jsonify({
            "status": "ok",
            "pagina": url,
            "modo": "somente_descoberta",
            "chamadas_openai": 0,
            "candidatos_para_revisao": True,
            "total_links": len(links),
            "links": links
        })

    except ValueError:
        return jsonify({"status": "erro", "detalhe": "URL ou resposta do crawler inválida"}), 400
    except Exception:
        return jsonify({
            "status": "erro",
            "detalhe": "Falha ao descobrir URLs no Swipefile"
        }), 500
@app.route('/swipes', methods=['GET'])
def swipes():
    categoria = request.args.get("categoria", "copywriting").lower()
    print(f"[DEBUG] /swipes requisitado com categoria: {categoria}")
    itens = carregar_swipes_postgres(categoria)
    return jsonify({
        "type": "cards",
        "title": f"Swipes da categoria: {categoria}",
        "items": itens
    })
@app.route('/buscar-swipes', methods=['GET'])
def buscar_swipes_endpoint():
    categoria = request.args.get("categoria")
    objetivo = request.args.get("objetivo")
    emocao = request.args.get("emocao")
    tom = request.args.get("tom")
    limite = request.args.get("limite", 5)

    resultados = buscar_swipes(
        categoria=categoria,
        objetivo=objetivo,
        emocao=emocao,
        tom=tom,
        limite=limite
    )

    return jsonify({
        "type": "cards",
        "title": "Swipes recomendados para o briefing",
        "filters": {
            "categoria": categoria,
            "objetivo": objetivo,
            "emocao": emocao,
            "tom": tom
        },
        "total": len(resultados),
        "items": resultados
    })
@app.route('/categorias', methods=['GET'])
def listar_categorias():
    categorias = listar_categorias_postgres()
    categorias_ordenadas = sorted(categorias)
    lista_texto = "\n".join([f"{i+1}. {categoria.capitalize()}" for i, categoria in enumerate(categorias_ordenadas)])
    print("[DEBUG] /categorias requisitado")
    return jsonify({
        "type": "text",
        "content": f"Escolha uma categoria digitando o número correspondente:\n\n{lista_texto}"
    })

@app.route('/estruturas/cards', methods=['GET'])
def obter_estrutura_copy_card():
    categoria = request.args.get("categoria", "").lower()
    print(f"[DEBUG] /estruturas/cards requisitado com categoria: {categoria}")

    if not categoria:
        return jsonify({"erro": "Categoria não informada"}), 400

    return jsonify(cards_para_categoria(categoria))

@app.route('/db-status', methods=['GET'])
def db_status():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        return jsonify({
            "status": "erro",
            "database": "nao_configurado"
        }), 500

    try:
        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM swipes;")
                total = cursor.fetchone()[0]

        return jsonify({
            "status": "ok",
            "database": "postgresql",
            "tabela": "swipes",
            "total_swipes": total
        })

    except Exception as e:
        return jsonify({
            "status": "erro",
            "database": "postgresql",
            "detalhe": str(e)
        }), 500
@app.route('/seed-db', methods=['GET'])
def seed_db():
    try:
        from seed_db import seed_database
        seed_database()
        return jsonify({
            "status": "ok",
            "message": "Seed do PostgreSQL concluído"
        })
    except Exception as e:
        return jsonify({
            "status": "erro",
            "detalhe": str(e)
        }), 500
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
