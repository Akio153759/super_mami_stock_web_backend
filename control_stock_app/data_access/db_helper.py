from django.db import connections
from django.db.utils import DEFAULT_DB_ALIAS, load_backend
import logging

_log = logging.getLogger('control_stock_app')


def create_connection(alias=DEFAULT_DB_ALIAS):
    """Retorna una nueva conexion a la base

    Args:
        alias ([string]): [Nombre default de la base de datos del diccionario de conexiones]

    Returns:
        [django.db.connection]: [Retorna un objeto de conexion de backend.oracle]
    """
    
    connections.ensure_defaults(alias)
    connections.prepare_test_settings(alias)
    db = connections.databases[alias]
    backend = load_backend(db['ENGINE'])
    
    return backend.DatabaseWrapper(db, alias)


def get_data_from_procedure(connection, proc_name, **kwargs):

    """
    Funcion que retorna lista de datos desde un procedimiento almacenado

    :param connection: conexion django
    :param proc_name: nombre del procedimiento almacenado a consultar
    :param kwargs: (proc_params: indica la lista de parametros que se asocian al procedimiento almacenado)
    :return: Lista con los datos en formato diccionario
    """

    lst_resultado = []

    with connection.cursor() as cur:

        try:


            _proc_params = kwargs.get('proc_params')

            if _proc_params is None:

                # ejecuto el store procedure sin parametros
                cur.callproc(proc_name)

            else:

                # asigno el cursor a la variable de salida
                #_proc_params['out_param'] = rawCursor

                # convierto a lista los elementos del diccionario (no necesito el key)
                _params = list(_proc_params.values())

                # ejecuto el store procedure con los parametros
                cur.callproc(proc_name, _params)

            # convierto el resultado a lista de diccionarios
            lst_resultado = get_dict_from_cursor(cur)

        except Exception as e:
            _log.error("Error en ejecucion de proceso get_data_from_procedure")
            _log.error("Procedimiento: " + proc_name)
            _log.error(str(e))

        finally:
            try:
                cur.close()
                # _log.debug("cursor cerrado")
                
            except Exception as e:
                _log.error('Error al cerrar cursor: Procedimiento: ' + proc_name)
                _log.error(str(e))
                
    return lst_resultado


def set_data_from_procedure(connection, proc_name, **kwargs):

    """
    Funcion que inserta/actualiza datos desde un procedimiento almacenado

    :param connection: conexion django
    :param proc_name: nombre del procedimiento almacenado a ejecutar
    :param kwargs: (proc_params: indica la lista de parametros que se asocian al procedimiento almacenado)
    """

    with connection.cursor() as cur:

        _proc_params = kwargs.get('proc_params')

        try:

            if _proc_params is None:

                # ejecuto el store procedure sin parametros
                cur.callproc(proc_name)

            else:

                # convierto a lista los elementos del diccionario (no necesito el key)
                _params = list(_proc_params.values())

                # ejecuto el store procedure con los parametros
                cur.callproc(proc_name, _params)

        except Exception as e:
            _log.error("Error ejecutandoSP: " + proc_name)
            _log.error(str(e))

        finally:
            cur.close()


def get_dict_from_cursor(cursor):

    """
    Retorna el resultado del cursor en una lista de diccionario
    :param cursor: cursor resultado de la ejecucion del query
    :return: lista de diccionario
    """

    lst_result = []

    try:

        # se obtienen los nombres de las columnas asociadas al resultado de la consulta
        cols = [col[0] for col in cursor.description]

        # por cada registro se arma el diccionario y se lo agrega a la lista
        for datarow in cursor:
            # print(datarow)
            lst_result.append(dict(zip(cols, datarow)))

    except Exception as e:
        _log.error("")
        _log.error("Error en el proceso: get_dict_from_cursor")
        _log.error(str(e))
        _log.error("")

    return lst_result
