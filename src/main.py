from contextlib import asynccontextmanager
from typing import AsyncGenerator, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Body, FastAPI, status, HTTPException, Depends
from fastapi.responses import RedirectResponse 
from fastapi.middleware.cors import CORSMiddleware

from database.db import engine, new_session
from database.models import Base
from database.crud import (
    add_owner_to_database, get_owners_from_db, 
    get_places_from_db, add_place_to_db,
    get_services_from_db, add_service_to_db,
    get_payments_from_db, add_payment_to_db,
    get_meterkinds_from_db, add_meterkind_to_db,
    get_meters_from_db, add_meter_to_db,
    get_cutoffs_from_db, add_cutoff_to_db
)    
from exceptions import (
    OwnerAlreadyExistsError, NoOwnersFoundError, 
    NoPlacesFoundError, PlaceAddError,
    NoServicesFoundError, ServiceAddError,
    NoPaymentsFoundError, PaymentAddError,
    NoMeterKindsFoundError, MeterKindAddError,
    NoMetersFoundError, MeterAddError,
    NoCutoffsFoundError, CutoffAddError
)
import datetime
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Skipping table dropping and recreating")
    # async with engine.begin() as connection:
    #     await connection.run_sync(Base.metadata.drop_all) 
    #     await connection.run_sync(Base.metadata.create_all) 
    yield # код до yield выполняется до старта веб-сервера. код после yield - после завершения работы веб-сервера


app = FastAPI(lifespan=lifespan)
# app.add_middleware(CORSMiddleware, allow_origins=["*"])

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    # async with new_session as session:
    #     yield session
    session = new_session()
    try:
        yield session
    finally:
        await session.close()    


@app.get("/owners",
         tags=["Владельцы"],
         summary="Выборка всех владельцев")
async def read_all_owners(
    session: Annotated[AsyncSession, Depends(get_session)]
):
    try:
        owners = await get_owners_from_db(session)
    except NoOwnersFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No owners found")
    return owners

@app.post("/owners",
         tags=["Владельцы"],
         summary="Добавление нового владельца")
async def post_owner(name: Annotated[str, Body(embed=True)],
               session: Annotated[AsyncSession, Depends(get_session)],
):
    print(f"trying to call add_owner_to_database with {name}")
    try:
        owner_id = await add_owner_to_database(name, session)
    except   OwnerAlreadyExistsError:
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cannot create owner {name=}"
        )
    return {"owner_id": owner_id}


@app.get("/places",
         tags=["Места возникновения затрат"],
         summary="Выборка всех Мест возникновения затрат")
async def read_all_places(
    session: Annotated[AsyncSession, Depends(get_session)]
):
    try:
        places = await get_places_from_db(session)
    except NoPlacesFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No places found")
    return places

@app.post("/places",
         tags=["Места возникновения затрат"],
         summary="Добавление Места возникновения затрат")
async def post_place(
    owner_id: Annotated[int, Body(embed=True)],
    name: Annotated[str, Body(embed=True)],
    address: Annotated[str, Body(embed=True)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    print(f"trying to call add_place_to_db with {name}")
    try:
        place_id = await add_place_to_db(owner_id, name, address, session)
    except PlaceAddError:
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cannot create place {name=} for owner {owner_id=}"
        )
    return {"place_id": place_id}


@app.get("/services",
         tags=["Оплачиваемые услуги по МВЗ"],
         summary="Выборка всех оплачиваемых услуг")
async def read_all_services(
    session: Annotated[AsyncSession, Depends(get_session)]
):
    try:
        services = await get_services_from_db(session)
    except NoServicesFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No services found")
    return services

@app.post("/services",
         tags=["Оплачиваемые услуги по МВЗ"],
         summary="Добавление Услуги")
async def post_service(
    place_id: Annotated[int, Body(embed=True)],
    name: Annotated[str, Body(embed=True)],
    accnum: Annotated[str, Body(embed=True)],
    cmt: Annotated[str, Body(embed=True)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    print(f"trying to call add_service_to_db with {name}")
    try:
        service_id = await add_service_to_db(place_id, name, accnum, cmt, session)
    except ServiceAddError:
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cannot create service {name=} for place {place_id=}"
        )
    return {"service_id": service_id, "place_id": place_id}

@app.get("/payments",
         tags=["Факты оплаты"],
         summary="Выборка всех фактов оплаты")
async def read_all_payments(
    session: Annotated[AsyncSession, Depends(get_session)]
):
    try:
        payments = await get_payments_from_db(session)
    except NoPaymentsFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No payments found")
    return payments

@app.post("/payments",
         tags=["Факты оплаты"],
         summary="Добавление факта оплаты")
async def post_payment(
    service_id: Annotated[int, Body(embed=True)],
    amount: Annotated[float, Body(embed=True)],
    pay_date: Annotated[datetime.date, Body(embed=True)],
    service_start_date: Annotated[datetime.date, Body(embed=True)] = None,
    service_finish_date: Annotated[datetime.date, Body(embed=True)] = None,
    cmt: Annotated[str, Body(embed=True, max_length=256)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
):
    print(f"trying to call add_payment_to_db with {amount=}")
    try:
        payment_id = await add_payment_to_db(service_id, amount, pay_date, service_start_date, service_finish_date, cmt, session)
    except PaymentAddError:
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cannot create payment {amount=} for service {service_id=}"
        )
    return {"payment_id" : payment_id, "service_id": service_id}



@app.get("/meterkinds",
         tags=["Виды приборов учёта"],
         summary="Выборка всех Видов приборов учёта")
async def read_all_meterkinds(
    session: Annotated[AsyncSession, Depends(get_session)]
):
    try:
        owners = await get_meterkinds_from_db(session)
    except NoMeterKindsFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No meterkinds found")
    return owners

@app.post("/meterkinds",
         tags=["Виды приборов учёта"],
         summary="Добавление нового Вида приборов учёта")
async def post_meterkind(name: Annotated[str, Body(embed=True)],
               session: Annotated[AsyncSession, Depends(get_session)],
):
    print(f"trying to call add_meterkind_to_database with {name}")
    try:
        meterkind_id = await add_meterkind_to_db(name, session)
    except   MeterKindAddError:
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cannot create meterkind {name=}"
        )
    return {"meterkind_id": meterkind_id}


@app.get("/meters",
         tags=["Приборы учёта (счетчики)"],
         summary="Выборка всех приборов учёта")
async def read_all_meters(
    session: Annotated[AsyncSession, Depends(get_session)]
):
    try:
        meters = await get_meters_from_db(session)
    except NoMetersFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No meters found")
    return meters

@app.post("/meters",
         tags=["Приборы учёта (счетчики)"],
         summary="Добавление Прибора учёта")
async def post_meter(
    place_id: Annotated[int, Body(embed=True)],
    meterkind_id: Annotated[int, Body(embed=True)],
    name: Annotated[str, Body(embed=True)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    print(f"trying to call add_meter_to_db with {name}")
    try:
        meter_id = await add_meter_to_db(place_id, meterkind_id, name, session)
    except MeterAddError:
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cannot create meter {name=} for place {place_id=}"
        )
    return {"meter_id": meter_id, "place_id": place_id}


@app.get("/cutoffs",
         tags=["Показания приборов учёта"],
         summary="Выборка всех показаний приборов учёта")
async def read_all_cutoffs(
    session: Annotated[AsyncSession, Depends(get_session)]
):
    try:
        cutoffs = await get_cutoffs_from_db(session)
    except NoCutoffsFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No cutoffs found")
    return cutoffs

@app.post("/cutoffs",
         tags=["Показания приборов учёта"],
         summary="Добавление Показания приборов учёта")
async def post_cutoff(
    meter_id: Annotated[int, Body(embed=True)],
    value: Annotated[float, Body(embed=True)],
    read_date: Annotated[datetime.date, Body(embed=True)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    print(f"trying to call add_cutoff_to_db with {value=}")
    try:
        cutoff_id = await add_cutoff_to_db(meter_id, value, read_date, session)
    except CutoffAddError:
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cannot create cutoff {value=} for meter {meter_id=}"
        )
    return {"cutoff_id": cutoff_id, "meter_id": meter_id}


@app.post("/ddl/create",
         tags=["DDL"],
         summary="Создание БД")
async def post_ddl_create(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    print(f"trying to create tables")
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all) 
    except :
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cannot create database tables"
        )
    return {"result": "ok"}

@app.post("/ddl/drop",
         tags=["DDL"],
         summary="Удаление БД")
async def post_ddl_drop(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    print(f"trying to create tables")
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all) 
    except :
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cannot create database tables"
        )
    return {"result": "ok"}


# Вспомогательный метод - заполнение БД
@app.post("/testdata",
         tags=["Наполнение пустой базы тестовыми данными"],
         summary="Добавление Владельца, МВЗ, услуг")
async def post_testdata(
    session: Annotated[AsyncSession, Depends(get_session)],
):

    print("Adding data")
    try:
        owner_id = await add_owner_to_database("Alx", session)
        print(f"Added owner {owner_id=}")
        place_id = await add_place_to_db(owner_id, "Квартира Питер", "Приморский 54-2-47 auto", session)
        print(f"Added place {place_id=}")
        service_id = await add_service_to_db(place_id, "ЖКУ ЕИРЦ", "71500287511", "ПЭС  телефон . S_1", session)
        print(f"Added service {service_id=}")
        service_id = await add_service_to_db(place_id, "ЖКУ Пионер", "10540201450047", "Пионер-Сервис Север (СПб)", session)
        print(f"Added service {service_id=}")
        service_id = await add_service_to_db(place_id, "Машиноместо", "", "", session)
        print(f"Added service {service_id=}")
        service_id = await add_service_to_db(place_id, "Кладовка", "", "", session)
        print(f"Added service {service_id=}")
        service_id = await add_service_to_db(place_id, "Интернет", "0000-000-004-255", "www-old.telixnet.ru-lk 1251069", session)
        print(f"Added service {service_id=}")
        service_id = await add_service_to_db(place_id, "Ипотека", "", "Погашение по 17 числам", session)
        print(f"Added service {service_id=}")
        place_id = await add_place_to_db(owner_id, "Квартира Москва", "16 Парковая 19-3-158 auto", session)
        print(f"Added place {place_id=}")
        service_id = await add_service_to_db(place_id, "Коммуналка", "", "", session)
        print(f"Added service {service_id=}")
        service_id = await add_service_to_db(place_id, "МосЭнергоСбыт", "", "", session)
        print(f"Added service {service_id=}")
        service_id = await add_service_to_db(place_id, "Интернет 2Ком", "165844", "almatel.ru-lk-oplata.php; user165844 - 15x6xwej", session)
        print(f"Added service {service_id=}")
        place_id = await add_place_to_db(owner_id, "Квартира Дедовск", "Курочкина 9-46 auto", session)
        print(f"Added place {place_id=}")
        service_id = await add_service_to_db(place_id, "Коммуналка", "", "Оплата до 10 числа", session)
        print(f"Added service {service_id=}")
        service_id = await add_service_to_db(place_id, "Интернет Алмател", "alx", "alxLove15x6xwej", session)
        print(f"Added service {service_id=}")
        place_id = await add_place_to_db(owner_id, "Аэромобилком - Экомобайл", "Платить со сбера на мобильного оператора Экомобайл", session)
        print(f"Added place {place_id=}")
        service_id = await add_service_to_db(place_id, "(903)0185013", "", "", session)
        print(f"Added service {service_id=}")
        service_id = await add_service_to_db(place_id, "(903)0185083", "", "", session)
        print(f"Added service {service_id=}")
        service_id = await add_service_to_db(place_id, "(903)0185281", "", "", session)
        print(f"Added service {service_id=}")
        service_id = await add_service_to_db(place_id, "(903)1251069", "", "", session)
        print(f"Added service {service_id=}")
        service_id = await add_service_to_db(place_id, "(905)5781544", "", "", session)
        print(f"Added service {service_id=}")

        place_id = await add_place_to_db(owner_id, "Toyota Land Cruiser Prado", "261", session)
        print(f"Added place {place_id=}")
        service_id = await add_service_to_db(place_id, "ОСАГО", "", "Оплата 18/02", session)
        print(f"Added service {service_id=}")
        service_id = await add_service_to_db(place_id, "КАСКО", "", "Оплата 18/02", session)
        print(f"Added service {service_id=}")

        place_id = await add_place_to_db(owner_id, "Honda Silver Wing 400", "", session)
        print(f"Added place {place_id=}")
        service_id = await add_service_to_db(place_id, "ОСАГО", "", "", session)
        print(f"Added service {service_id=}")

        place_id = await add_place_to_db(owner_id, "Kawasaki Ninja 650", "", session)
        print(f"Added place {place_id=}")
        service_id = await add_service_to_db(place_id, "ОСАГО", "", "", session)
        print(f"Added service {service_id=}")

        place_id = await add_place_to_db(owner_id, "Honda NC750", "", session)
        print(f"Added place {place_id=}")
        service_id = await add_service_to_db(place_id, "ОСАГО", "", "", session)
        print(f"Added service {service_id=}")

        hw_meterkind_id = await add_meterkind_to_db("ГВС", session)
        print(f"Added meterkind {hw_meterkind_id=}")
        cw_meterkind_id = await add_meterkind_to_db("ХВС", session)
        print(f"Added meterkind {cw_meterkind_id=}")
        ed_meterkind_id = await add_meterkind_to_db("ЭЭ День", session)
        print(f"Added meterkind {ed_meterkind_id=}")
        en_meterkind_id = await add_meterkind_to_db("ЭЭ Ночь", session)
        print(f"Added meterkind {en_meterkind_id=}")
        meter_id = await add_meter_to_db(place_id, cw_meterkind_id, "17-0409066", session)
        print(f"Added meterkind {meter_id=}")
        meter_id = await add_meter_to_db(place_id, cw_meterkind_id, "17-0409074", session)
        print(f"Added meterkind {meter_id=}")
        meter_id = await add_meter_to_db(place_id, hw_meterkind_id, "17-0409062", session)
        print(f"Added meterkind {meter_id=}")
        meter_id = await add_meter_to_db(place_id, hw_meterkind_id, "17-0409071", session)
        print(f"Added meterkind {meter_id=}")
        meter_id = await add_meter_to_db(place_id, ed_meterkind_id, "33272530", session)
        print(f"Added meterkind {meter_id=}")
        meter_id = await add_meter_to_db(place_id, en_meterkind_id, "33272530", session)
        print(f"Added meterkind {meter_id=}")
    except PlaceAddError:
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cannot create place"
        )
    except ServiceAddError:
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cannot create service"
        )
    except OwnerAlreadyExistsError:
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cannot create owner"
        )
    except MeterKindAddError:
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cannot create meter kind"
        )
    except MeterAddError:
        raise HTTPException( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cannot create meter"
        )
    finally:
        print("Finished adding data")

    return {"owner_id": owner_id, "place_id": place_id, "service_id": service_id, "en_meterkind_id": en_meterkind_id, "meter_id": meter_id}


if __name__ == "__main__":
    uvicorn.run("main:app", reload = True)
