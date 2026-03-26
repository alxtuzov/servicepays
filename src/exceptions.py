class HomePaymentsBaseError(Exception):
    pass

class NoOwnerFoundError(HomePaymentsBaseError):
    pass

class OwnerAlreadyExistsError(HomePaymentsBaseError):
    pass

class NoOwnersFoundError(HomePaymentsBaseError):
    pass

class PlaceAddError(HomePaymentsBaseError):
    pass

class NoPlacesFoundError(HomePaymentsBaseError):
    pass

class ServiceAddError(HomePaymentsBaseError):
    pass

class NoServicesFoundError(HomePaymentsBaseError):
    pass

class PaymentAddError(HomePaymentsBaseError):
    pass

class NoPaymentsFoundError(HomePaymentsBaseError):
    pass

class MeterKindAddError(HomePaymentsBaseError):
    pass

class NoMeterKindsFoundError(HomePaymentsBaseError):
    pass

class MeterAddError(HomePaymentsBaseError):
    pass

class NoMetersFoundError(HomePaymentsBaseError):
    pass

class CutoffAddError(HomePaymentsBaseError):
    pass

class NoCutoffsFoundError(HomePaymentsBaseError):
    pass
