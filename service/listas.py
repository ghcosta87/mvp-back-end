from http import HTTPStatus
import model.constants as const
from model.lista import ListaDeCompras
import logging


def check_duplicate(sessionImport, table, item):
    return sessionImport.query(table).filter_by(titulo=item).first()


def return_error(schema, error,session):
    session.rollback()
    logging.error(error)
    return (
        schema(message=const.ERRO_INTERNO, error=str(error)).model_dump(),
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )
