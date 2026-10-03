from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/sync-produtos")
def sincronizar_produtos(request: Request):
    container = request.app.state.container
    try:
        total = container.sincronizar_catalogo_usecase.executar(container.settings.produtos_xlsx)
    except FileNotFoundError as erro:
        raise HTTPException(status_code=400, detail=str(erro))
    return {"ok": True, "produtos_sincronizados": total}
