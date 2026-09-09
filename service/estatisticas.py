from model.produto import Produto
from sqlalchemy import func

def obter_estatisticas_produtos(session):
    
    estatisticas = (
        session.query(
            Produto.nome, # a coluna nome da tabela mapeada por esta classe"
            func.count(Produto.id).label("total_compras"),
            func.avg(Produto.preco).label("preco_medio"),
            func.min(Produto.preco).label("menor_preco"),
            func.max(Produto.preco).label("maior_preco"),
        )
        .group_by(Produto.nome)
        .all()
    )

    for linha in estatisticas:
        print(linha.nome, linha.total_compras, linha.preco_medio)
        
    return estatisticas