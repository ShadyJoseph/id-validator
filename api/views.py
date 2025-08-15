from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import NationalIDSerializer
from .models import Log
from .authentication import ApiKeyAuthentication
from .permissions import HasApiKey
from .throttling import ApiKeyRateThrottle


def validate_and_extract(nid: str) -> dict:
    """Validate Egyptian national ID and extract information."""
    if not nid.isdigit() or len(nid) != 14:
        raise ValueError("National ID must be exactly 14 digits")

    p = nid[0]
    if p not in ('2', '3'):
        raise ValueError("Invalid century digit (must be 2 or 3)")

    yy = nid[1:3]
    mm = nid[3:5]
    dd = nid[5:7]
    rr = nid[7:9]
    ssss = nid[9:13]
    # c = nid[13]  # Check digit not validated (optional as per sources)

    # Governorate codes
    gov_codes = {
        '01': 'Cairo', '02': 'Alexandria', '03': 'Port Said', '04': 'Suez',
        '11': 'Damietta', '12': 'Dakahlia', '13': 'Sharkia', '14': 'Qalyubia',
        '15': 'Kafr El Sheikh', '16': 'Gharbia', '17': 'Monufia', '18': 'Beheira',
        '19': 'Ismailia', '21': 'Giza', '22': 'Beni Suef', '23': 'Fayoum',
        '24': 'Minya', '25': 'Assiut', '26': 'Sohag', '27': 'Qena',
        '28': 'Aswan', '29': 'Luxor', '31': 'Red Sea', '32': 'New Valley',
        '33': 'Matrouh', '34': 'North Sinai', '35': 'South Sinai', '88': 'Foreign'
    }
    if rr not in gov_codes:
        raise ValueError("Invalid governorate code")
    governorate = gov_codes[rr]

    # Gender from last digit of serial
    gender_digit = int(nid[12])
    gender = 'Male' if gender_digit % 2 == 1 else 'Female'

    # Birth date validation
    century = 1900 if p == '2' else 2000
    birth_year = century + int(yy)
    try:
        birth_date = datetime.strptime(
            f"{birth_year}-{mm}-{dd}", "%Y-%m-%d").date()
        if birth_date > datetime.now().date():
            raise ValueError("Birth date cannot be in the future")
    except ValueError:
        raise ValueError("Invalid birth date format or values")

    return {
        "birth_year": birth_year,
        "birth_date": birth_date.strftime("%d/%m/%Y"),
        "gender": gender,
        "governorate": governorate
    }


class NationalIDView(APIView):
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [HasApiKey]
    throttle_classes = [ApiKeyRateThrottle]

    def post(self, request):
        serializer = NationalIDSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        nid = serializer.validated_data['national_id']
        try:
            extracted = validate_and_extract(nid)
            valid = True
            error = None
        except ValueError as e:
            extracted = None
            valid = False
            error = str(e)

        # Log the call
        Log.objects.create(
            national_id=nid,
            valid=valid,
            extracted_data=extracted,
            error=error,
            api_key_used=request.user.key
        )

        if valid:
            return Response({"valid": True, **extracted})
        return Response({"valid": False, "error": error}, status=status.HTTP_400_BAD_REQUEST)
