from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
    OwnersOrm, PlacesOrm, ServicesOrm, PaymentsOrm, 
    MeterKindsOrm, MetersOrm, CutoffsOrm
)    
from exceptions import (
    OwnerAlreadyExistsError , PlaceAddError, ServiceAddError, PaymentAddError, 
    MeterKindAddError, MeterAddError, CutoffAddError
)
import datetime

async def add_owner_to_database(
    name: str,
    session: AsyncSession,
) -> int | None: 
    new_owner = OwnersOrm(
        name=name
    )
    session.add(new_owner)
    try:
        await session.commit() 
    except IntegrityError:
        raise OwnerAlreadyExistsError  # сюда лучше добавить логи
    return new_owner.id           
          
        
async def get_owner_by_id_from_db(
    owner_id: int,
    session: AsyncSession,
) -> str | None: 
    query = select(OwnersOrm).filter_by(id=owner_id)
    result = await session.execute(query) 
    res: OwnersOrm | None = result.scalar_one_or_none()
    return res.name if res.name else None

async def get_owners_from_db(
    session: AsyncSession,
) -> str | None: 
    query = select(OwnersOrm)
    result = await session.execute(query) 
    #return f"{result.scalars().all()=}"
    res = result.unique().scalars().all()
    return res
    

async def add_place_to_db(
    owner_id: int,
    name: str,
    address: str,
    session: AsyncSession,
) -> int | None: 
    new_place = PlacesOrm(
        owner_id = owner_id,
        name = name,
        address = address,
    )
    session.add(new_place)
    try:
        await session.commit() 
    except IntegrityError:
        raise PlaceAddError  # сюда лучше добавить логи
    return new_place.id           
          
        
async def get_places_from_db(
    session: AsyncSession,
) -> str | None: 
    query = select(PlacesOrm)
    result = await session.execute(query) 
    #return f"{result.scalars().all()=}"
    res = result.unique().scalars().all()
    return res
    
async def add_service_to_db(
    place_id: int,
    name: str,
    accnum: str,
    cmt: str,
    session: AsyncSession,
) -> int | None: 
    new_service = ServicesOrm(
        place_id = place_id,
        name = name,
        accnum = accnum,
        cmt = cmt,
    )
    session.add(new_service)
    try:
        await session.commit() 
    except IntegrityError:
        raise ServiceAddError  # сюда лучше добавить логи
    return new_service.id           
          
        
async def get_services_from_db(
    session: AsyncSession,
) -> str | None: 
    query = select(ServicesOrm)
    result = await session.execute(query) 
    #return f"{result.scalars().all()=}"
    res = result.unique().scalars().all()
    return res
    

async def add_payment_to_db(
    service_id: int,
    amount: float,
    pay_date: datetime.date,
    service_start_date: datetime.date,
    service_finish_date: datetime.date,
    cmt: str,
    session: AsyncSession,
) -> int | None: 
    new_payment = PaymentsOrm(
        service_id = service_id,
        amount = amount,
        pay_date = pay_date,
        service_start_date = service_start_date,
        service_finish_date = service_finish_date,
        cmt = cmt,
    )
    session.add(new_payment)
    try:
        await session.commit() 
    except IntegrityError:
        raise PaymentAddError  # сюда лучше добавить логи
    return new_payment.id           
          
        
async def get_payments_from_db(
    session: AsyncSession,
) -> str | None: 
    query = select(PaymentsOrm)
    result = await session.execute(query) 
    #return f"{result.scalars().all()=}"
    res = result.unique().scalars().all()
    return res
    

async def add_meterkind_to_db(
    name: str,
    session: AsyncSession,
) -> int | None: 
    new_meterkind = MeterKindsOrm(
        name = name,
    )
    session.add(new_meterkind)
    try:
        await session.commit() 
    except IntegrityError:
        raise MeterKindAddError  # сюда лучше добавить логи
    return new_meterkind.id           
       

async def get_meterkinds_from_db(
    session: AsyncSession,
) -> str | None: 
    query = select(MeterKindsOrm)
    result = await session.execute(query) 
    #return f"{result.scalars().all()=}"
    res = result.unique().scalars().all()
    return res

async def add_meter_to_db(
    place_id: int,
    meterkind_id: int,
    name: str,
    session: AsyncSession,
) -> int | None: 
    new_meter = MetersOrm(
        place_id = place_id,
        meterkind_id = meterkind_id, 
        name = name,
    )
    session.add(new_meter)
    try:
        await session.commit() 
    except IntegrityError:
        raise MeterAddError  # сюда лучше добавить логи
    return new_meter.id           
       
async def get_meters_from_db(
    session: AsyncSession,
) -> str | None: 
    query = select(MetersOrm)
    result = await session.execute(query) 
    #return f"{result.scalars().all()=}"
    res = result.unique().scalars().all()
    return res

async def add_cutoff_to_db(
    meter_id: int,
    value: float,
    read_date: datetime.date,
    session: AsyncSession,
) -> int | None: 
    new_cutoff = CutoffsOrm(
        meter_id = meter_id, 
        value = value,
        read_date = read_date,
    )
    session.add(new_cutoff)
    try:
        await session.commit() 
    except IntegrityError:
        raise CutoffAddError  # сюда лучше добавить логи
    return new_cutoff.id           
       
async def get_cutoffs_from_db(
    session: AsyncSession,
) -> str | None: 
    query = select(CutoffsOrm)
    result = await session.execute(query) 
    #return f"{result.scalars().all()=}"
    res = result.unique().scalars().all()
    return res

