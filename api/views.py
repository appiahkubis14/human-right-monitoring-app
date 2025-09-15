from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.utils import saveimage
from portal.models import *
from .serializers import *

# Utility decorator to check if staff exists
def staff_exists_required(view_func):
    def wrapper(request, *args, **kwargs):
        staff_id = request.data.get('user') or request.data.get('staffid')
        if not staff_id:
            return Response({'error': 'Staff ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            staff = staffTbl.objects.get(staffid=staff_id)
            request.staff = staff
            return view_func(request, *args, **kwargs)
        except staffTbl.DoesNotExist:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
    return wrapper

class StaffLoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Staff login authentication",
        request_body=StaffLoginSerializer,
        responses={
            200: openapi.Response('Login successful', StaffSerializer),
            400: 'Invalid credentials',
            500: 'Internal server error'
        }
    )
    def post(self, request):
        try:
            serializer = StaffLoginSerializer(data=request.data)
            if serializer.is_valid():
                staffid = serializer.validated_data['staffid']
                try:
                    staff = staffTbl.objects.get(staffid=staffid)
                    return Response({
                        'message': 'Login successful',
                        'staff': StaffSerializer(staff).data
                    }, status=status.HTTP_200_OK)
                except staffTbl.DoesNotExist:
                    return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @staff_exists_required
    @swagger_auto_schema(
        operation_description="Change staff user password",
        request_body=ChangePasswordSerializer,
        responses={
            200: 'Password changed successfully',
            400: 'Bad request',
            500: 'Internal server error'
        }
    )
    def post(self, request):
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            if serializer.is_valid():
                staff_id = serializer.validated_data['user']
                new_password = serializer.validated_data['new_password']
                
                try:
                    staff = staffTbl.objects.get(staffid=staff_id)
                    staff.cmpassword = new_password
                    staff.save()
                    return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
                except staffTbl.DoesNotExist:
                    return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StaffAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get all staff members",
        responses={200: StaffSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            staff_query = staffTbl.objects.all()
            serializer = StaffSerializer(staff_query, many=True)
            return Response({'msg': "Staff data fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StaffDetailAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get staff member by ID",
        responses={200: StaffSerializer, 404: "Staff not found", 500: "Internal Server Error"}
    )
    def get(self, request, staff_id):
        try:
            staff = staffTbl.objects.get(id=staff_id)
            serializer = StaffSerializer(staff)
            return Response({'msg': "Staff data fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except staffTbl.DoesNotExist:
            return Response({'msg': "Staff not found", 'data': {}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FarmerAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get all farmers",
        responses={200: FarmerSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            farmers = farmerTbl.objects.all()
            serializer = FarmerSerializer(farmers, many=True)
            return Response({'msg': "Farmers data fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FarmerDetailAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get farmer by ID",
        responses={200: FarmerSerializer, 404: "Farmer not found", 500: "Internal Server Error"}
    )
    def get(self, request, farmer_id):
        try:
            farmer = farmerTbl.objects.get(id=farmer_id)
            serializer = FarmerSerializer(farmer)
            return Response({'msg': "Farmer data fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except farmerTbl.DoesNotExist:
            return Response({'msg': "Farmer not found", 'data': {}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PCIAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Create PCI data",
        request_body=PCISerializer,
        responses={
            201: 'PCI data created successfully', 
            400: "Invalid data", 
            500: "Internal Server Error"
        }
    )
    def post(self, request):
        """
        Create a new PCI record.

        The record must contain the following information:
        - `enumerator`: The enumerator who collected the data
        - `society`: The society being assessed
        - `access_to_protected_water`: Access to protected water source (0-1)
        - `hire_adult_labourers`: Hiring of adult labourers (0-1)
        - `awareness_raising_session`: Awareness raising sessions conducted (0-1)
        - `women_leaders`: Presence of women leaders (0-1)
        - `pre_school`: Presence of pre-school (0-1)
        - `primary_school`: Presence of primary school (0-1)
        - `separate_toilets`: Separate toilets in schools (0-1)
        - `provide_food`: School provides food (0-1)
        - `scholarships`: Availability of scholarships (0-1)
        - `corporal_punishment`: Absence of corporal punishment (0-1)

        The endpoint will automatically calculate the total index and risk status.

        Returns:
        - 201: PCI record created successfully
        - 400: Invalid data provided
        - 500: Internal server error
        """
        try:
            data = request.data.copy()
            
            # Convert string values to Decimal if needed
            decimal_fields = [
                'access_to_protected_water', 'hire_adult_labourers', 
                'awareness_raising_session', 'women_leaders', 'pre_school',
                'primary_school', 'separate_toilets', 'provide_food',
                'scholarships', 'corporal_punishment'
            ]
            
            for field in decimal_fields:
                if field in data and data[field] is not None:
                    try:
                        data[field] = Decimal(str(data[field]))
                    except (ValueError, TypeError):
                        return Response(
                            {'msg': f"Invalid value for {field}. Must be a number.", 'data': {}}, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
            
            serializer = PCISerializer(data=data)
            if serializer.is_valid():
                # Save the instance first
                pci_instance = serializer.save()
                
                # Calculate total index and status
                pci_instance.calculate_total_index()
                
                # Return the updated data
                updated_serializer = PCISerializer(pci_instance)
                return Response(
                    {'msg': "PCI data created successfully", 'data': updated_serializer.data}, 
                    status=status.HTTP_201_CREATED
                )
            
            return Response(
                {'msg': serializer.errors, 'data': {}}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {'msg': f"Internal server error: {str(e)}", 'data': {}}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Get all PCI data",
        responses={
            200: PCISerializer(many=True), 
            500: "Internal Server Error"
        }
    )
    def get(self, request):
        """
        Get all PCI records.

        Returns a list of all PCI assessments with their calculated risk levels.

        Returns:
        - 200: List of PCI records
        - 500: Internal server error
        """
        try:
            pci_data = pciTbl.objects.all()
            serializer = PCISerializer(pci_data, many=True)
            return Response(
                {'msg': "PCI data fetched successfully", 'data': serializer.data}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'msg': f"Internal server error: {str(e)}", 'data': []}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        



class PCIDetailAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get PCI data by ID",
        responses={200: PCISerializer, 404: "PCI data not found", 500: "Internal Server Error"}
    )
    def get(self, request, pci_id):
        try:
            pci = pciTbl.objects.get(id=pci_id)
            serializer = PCISerializer(pci)
            return Response({'msg': "PCI data fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except pciTbl.DoesNotExist:
            return Response({'msg': "PCI data not found", 'data': {}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HouseholdAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Create household survey data",
        request_body=HouseholdSerializer,
        responses={201: 'Household data created successfully', 400: "Invalid data", 500: "Internal Server Error"}
    )
    
    def post(self, request):
        try:
            data = request.data
            # print(data)
            if data.get('signature_producer'):
                data['signature_producer'] = saveimage(data['signature_producer'], 'signature_producer')
            if data.get('picture_sensitization'):
                data['picture_sensitization'] = saveimage(data['picture_sensitization'], 'picture_sensitization')
            
            serializer = HouseholdSerializer(data=data)
            print(serializer)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': "Household data created successfully", 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'msg': serializer.errors, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Get all household surveys",
        responses={200: HouseholdSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            households = houseHoldTbl.objects.all()
            serializer = HouseholdSerializer(households, many=True)
            return Response({'msg': "Household data fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HouseholdDetailAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get household survey by ID",
        responses={200: HouseholdSerializer, 404: "Household not found", 500: "Internal Server Error"}
    )
    def get(self, request, household_id):
        try:
            household = houseHoldTbl.objects.get(id=household_id)
            serializer = HouseholdSerializer(household)
            return Response({'msg': "Household data fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except houseHoldTbl.DoesNotExist:
            return Response({'msg': "Household not found", 'data': {}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class AdultHouseholdMemberAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Create adult household member",
        request_body=AdultHouseholdMemberSerializer,
        responses={
            201: 'Adult household member created successfully', 
            400: "Invalid data", 
            500: "Internal Server Error"
        }
    )
    def post(self, request):
        """
        Create a new adult household member record.

        Required fields:
        - `houseHold`: ID of the household this member belongs to
        - `full_name`: Full name of the adult member
        - `relationship`: Relationship to the respondent
        - `gender`: Gender of the member
        - `nationality`: Nationality of the member
        - `year_birth`: Year of birth (1900-current year)
        - `birth_certificate`: Whether the member has a birth certificate
        - `main_work`: Main work/occupation

        Optional fields:
        - `relationship_other`: Specify relationship if 'Other' is selected
        - `country_origin`: Country of origin if non-Ghanaian
        - `country_origin_other`: Specify country if 'Other' is selected
        - `main_work_other`: Specify main work if 'Other' is selected

        Returns:
        - 201: Adult member created successfully
        - 400: Invalid data provided
        - 500: Internal server error
        """
        try:
            data = request.data.copy()
            
            # Validate household exists
            household_id = data.get('houseHold')
            if household_id:
                try:
                    household = houseHoldTbl.objects.get(id=household_id)
                    data['houseHold'] = household.id
                except houseHoldTbl.DoesNotExist:
                    return Response(
                        {'msg': "Household not found", 'data': {}}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            serializer = AdultHouseholdMemberSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'msg': "Adult household member created successfully", 'data': serializer.data}, 
                    status=status.HTTP_201_CREATED
                )
            
            return Response(
                {'msg': serializer.errors, 'data': {}}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {'msg': f"Internal server error: {str(e)}", 'data': {}}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Get all adult household members",
        responses={
            200: AdultHouseholdMemberSerializer(many=True), 
            500: "Internal Server Error"
        }
    )
    def get(self, request):
        """
        Get all adult household member records.

        Optional query parameters:
        - `household_id`: Filter by specific household ID
        - `relationship`: Filter by relationship type

        Returns:
        - 200: List of adult household members
        - 500: Internal server error
        """
        try:
            # Get optional filter parameters
            household_id = request.GET.get('household_id')
            relationship = request.GET.get('relationship')
            
            adults = AdultHouseholdMember.objects.all()
            
            # Apply filters if provided
            if household_id:
                adults = adults.filter(houseHold_id=household_id)
            if relationship:
                adults = adults.filter(relationship=relationship)
            
            serializer = AdultHouseholdMemberSerializer(adults, many=True)
            return Response(
                {'msg': "Adult household members fetched successfully", 'data': serializer.data}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'msg': f"Internal server error: {str(e)}", 'data': []}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdultHouseholdMemberDetailAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get adult household member by ID",
        responses={
            200: AdultHouseholdMemberSerializer, 
            404: "Adult household member not found", 
            500: "Internal Server Error"
        }
    )
    def get(self, request, member_id):
        """
        Get a specific adult household member by ID.

        Parameters:
        - `member_id`: ID of the adult household member to retrieve

        Returns:
        - 200: Adult household member details
        - 404: Member not found
        - 500: Internal server error
        """
        try:
            adult_member = AdultHouseholdMember.objects.get(id=member_id)
            serializer = AdultHouseholdMemberSerializer(adult_member)
            return Response(
                {'msg': "Adult household member fetched successfully", 'data': serializer.data}, 
                status=status.HTTP_200_OK
            )
        except AdultHouseholdMember.DoesNotExist:
            return Response(
                {'msg': "Adult household member not found", 'data': {}}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'msg': f"Internal server error: {str(e)}", 'data': {}}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Update adult household member",
        request_body=AdultHouseholdMemberSerializer,
        responses={
            200: 'Adult household member updated successfully', 
            400: "Invalid data", 
            404: "Member not found",
            500: "Internal Server Error"
        }
    )
    def put(self, request, member_id):
        """
        Update an existing adult household member.

        Parameters:
        - `member_id`: ID of the adult household member to update

        Returns:
        - 200: Member updated successfully
        - 400: Invalid data provided
        - 404: Member not found
        - 500: Internal server error
        """
        try:
            adult_member = AdultHouseholdMember.objects.get(id=member_id)
            serializer = AdultHouseholdMemberSerializer(adult_member, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'msg': "Adult household member updated successfully", 'data': serializer.data}, 
                    status=status.HTTP_200_OK
                )
            
            return Response(
                {'msg': serializer.errors, 'data': {}}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except AdultHouseholdMember.DoesNotExist:
            return Response(
                {'msg': "Adult household member not found", 'data': {}}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'msg': f"Internal server error: {str(e)}", 'data': {}}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Delete adult household member",
        responses={
            200: 'Adult household member deleted successfully', 
            404: "Member not found",
            500: "Internal Server Error"
        }
    )
    def delete(self, request, member_id):
        """
        Delete an adult household member.

        Parameters:
        - `member_id`: ID of the adult household member to delete

        Returns:
        - 200: Member deleted successfully
        - 404: Member not found
        - 500: Internal server error
        """
        try:
            adult_member = AdultHouseholdMember.objects.get(id=member_id)
            adult_member.delete()
            return Response(
                {'msg': "Adult household member deleted successfully", 'data': {}}, 
                status=status.HTTP_200_OK
            )
        except AdultHouseholdMember.DoesNotExist:
            return Response(
                {'msg': "Adult household member not found", 'data': {}}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'msg': f"Internal server error: {str(e)}", 'data': {}}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# views.py
class ChildInHouseholdAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Create child in household data",
        request_body=ChildInHouseholdSerializer,
        responses={201: 'Child data created successfully', 400: "Invalid data", 500: "Internal Server Error"}
    )
    def post(self, request):
        try:
            data = request.data.copy()  # Create a copy to avoid modifying original
            
            # Convert numeric fields from string to appropriate types
            numeric_fields = ['child_identifier', 'child_year_birth', 'child_schl_left_age']
            
            for field in numeric_fields:
                if field in data and isinstance(data[field], str) and data[field].isdigit():
                    data[field] = int(data[field])
            
            # Handle sch_going_times specifically
            if 'sch_going_times' in data and isinstance(data['sch_going_times'], str):
                if data['sch_going_times'].isdigit():
                    data['sch_going_times'] = int(data['sch_going_times'])
                else:
                    # Keep as string if it's a choice code like '01', '02', etc.
                    pass
            
            # Handle performed_tasks if it's a string (comma-separated)
            if 'performed_tasks' in data and isinstance(data['performed_tasks'], str):
                if data['performed_tasks']:
                    data['performed_tasks'] = data['performed_tasks'].split(',')
                else:
                    data['performed_tasks'] = []
            
            serializer = ChildInHouseholdSerializer(data=data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'msg': "Child data created successfully", 
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'msg': "Validation failed", 
                'errors': serializer.errors,
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            print(f"Data received: {request.data}")
            return Response({
                'msg': f"Internal server error: {str(e)}", 
                'data': {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Get all children in households",
        responses={200: ChildInHouseholdSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            children = ChildInHouseholdTbl.objects.all()
            serializer = ChildInHouseholdSerializer(children, many=True)
            return Response({
                'msg': "Children data fetched successfully", 
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'msg': str(e), 
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class RegionAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get all regions",
        responses={200: RegionSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            regions = regionTbl.objects.all()
            serializer = RegionSerializer(regions, many=True)
            return Response({'msg': "Regions data fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DistrictAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get all districts",
        responses={200: DistrictSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            districts = districtTbl.objects.all()
            serializer = DistrictSerializer(districts, many=True)
            return Response({'msg': "Districts data fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SocietyAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get all societies",
        responses={200: SocietySerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            societies = societyTbl.objects.all()
            serializer = SocietySerializer(societies, many=True)
            return Response({'msg': "Societies data fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeadlineAssignmentAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Create deadline assignment",
        request_body=DeadlineAssignmentSerializer,
        responses={201: 'Deadline assignment created successfully', 400: "Invalid data", 500: "Internal Server Error"}
    )
    def post(self, request):
        try:
            data = request.data
            serializer = DeadlineAssignmentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': "Deadline assignment created successfully", 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'msg': serializer.errors, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Get all deadline assignments",
        responses={200: DeadlineAssignmentSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            deadlines = DeadlineAssignment.objects.all()
            serializer = DeadlineAssignmentSerializer(deadlines, many=True)
            return Response({'msg': "Deadline assignments fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QueryAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Create query",
        request_body=QuerySerializer,
        responses={201: 'Query created successfully', 400: "Invalid data", 500: "Internal Server Error"}
    )
    def post(self, request):
        try:
            data = request.data
            serializer = QuerySerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': "Query created successfully", 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'msg': serializer.errors, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Get all queries",
        responses={200: QuerySerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            queries = Query.objects.all()
            serializer = QuerySerializer(queries, many=True)
            return Response({'msg': "Queries fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RiskAssessmentAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Create risk assessment",
        request_body=RiskAssessmentSerializer,
        responses={201: 'Risk assessment created successfully', 400: "Invalid data", 500: "Internal Server Error"}
    )
    def post(self, request):
        try:
            data = request.data
            serializer = RiskAssessmentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': "Risk assessment created successfully", 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'msg': serializer.errors, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Get all risk assessments",
        responses={200: RiskAssessmentSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            assessments = RiskAssessment.objects.all()
            serializer = RiskAssessmentSerializer(assessments, many=True)
            return Response({'msg': "Risk assessments fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HealthCheckAPIView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="API health check",
        responses={200: 'API is healthy'}
    )
    def get(self, request):
        return Response({'status': 'healthy', 'timestamp': timezone.now().isoformat()})
    








# Light Task APIs
class LightTaskAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Create light task",
        request_body=LightTaskSerializer,
        responses={201: 'Light task created successfully', 400: "Invalid data", 500: "Internal Server Error"}
    )
    def post(self, request):
        try:
            data = request.data
            serializer = LightTaskSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': "Light task created successfully", 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'msg': serializer.errors, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Get all light tasks",
        responses={200: LightTaskSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            tasks = lightTaskTbl.objects.all()
            serializer = LightTaskSerializer(tasks, many=True)
            return Response({'msg': "Light tasks fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LightTaskDetailAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get light task by ID",
        responses={200: LightTaskSerializer, 404: "Light task not found", 500: "Internal Server Error"}
    )
    def get(self, request, task_id):
        try:
            task = lightTaskTbl.objects.get(id=task_id)
            serializer = LightTaskSerializer(task)
            return Response({'msg': "Light task fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except lightTaskTbl.DoesNotExist:
            return Response({'msg': "Light task not found", 'data': {}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Heavy Task APIs
class HeavyTaskAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Create heavy task",
        request_body=HeavyTaskSerializer,
        responses={201: 'Heavy task created successfully', 400: "Invalid data", 500: "Internal Server Error"}
    )
    def post(self, request):
        try:
            data = request.data
            serializer = HeavyTaskSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': "Heavy task created successfully", 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'msg': serializer.errors, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Get all heavy tasks",
        responses={200: HeavyTaskSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            tasks = heavyTaskTbl.objects.all()
            serializer = HeavyTaskSerializer(tasks, many=True)
            return Response({'msg': "Heavy tasks fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HeavyTaskDetailAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get heavy task by ID",
        responses={200: HeavyTaskSerializer, 404: "Heavy task not found", 500: "Internal Server Error"}
    )
    def get(self, request, task_id):
        try:
            task = heavyTaskTbl.objects.get(id=task_id)
            serializer = HeavyTaskSerializer(task)
            return Response({'msg': "Heavy task fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except heavyTaskTbl.DoesNotExist:
            return Response({'msg': "Heavy task not found", 'data': {}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Child Light Task APIs
class ChildLightTaskAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Create child light task record",
        request_body=ChildLightTaskSerializer,
        responses={201: 'Child light task created successfully', 400: "Invalid data", 500: "Internal Server Error"}
    )
    def post(self, request):
        try:
            data = request.data.copy()
            
            # Validate foreign key relationships
            if 'task' in data:
                try:
                    task = lightTaskTbl.objects.get(id=data['task'])
                    data['task'] = task.id
                except lightTaskTbl.DoesNotExist:
                    return Response({'msg': "Light task not found", 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
            
            if 'child' in data:
                try:
                    child = ChildInHouseholdTbl.objects.get(id=data['child'])
                    data['child'] = child.id
                except ChildInHouseholdTbl.DoesNotExist:
                    return Response({'msg': "Child not found", 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
            
            # Convert numeric fields
            int_fields = ['total_hours_light_work_school_12', 'total_hours_light_work_non_school_12']
            for field in int_fields:
                if field in data and data[field] is not None:
                    try:
                        data[field] = int(data[field])
                    except (ValueError, TypeError):
                        pass
            
            serializer = ChildLightTaskSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': "Child light task created successfully", 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'msg': serializer.errors, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Get all child light tasks",
        responses={200: ChildLightTaskSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            tasks = childLightTaskTbl.objects.all()
            serializer = ChildLightTaskSerializer(tasks, many=True)
            return Response({'msg': "Child light tasks fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Child Heavy Task APIs
class ChildHeavyTaskAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Create child heavy task record",
        request_body=ChildHeavyTaskSerializer,
        responses={201: 'Child heavy task created successfully', 400: "Invalid data", 500: "Internal Server Error"}
    )
    def post(self, request):
        try:
            data = request.data.copy()
            
            # Validate foreign key relationships
            if 'task' in data:
                try:
                    task = heavyTaskTbl.objects.get(id=data['task'])
                    data['task'] = task.id
                except heavyTaskTbl.DoesNotExist:
                    return Response({'msg': "Heavy task not found", 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
            
            if 'child' in data:
                try:
                    child = ChildInHouseholdTbl.objects.get(id=data['child'])
                    data['child'] = child.id
                except ChildInHouseholdTbl.DoesNotExist:
                    return Response({'msg': "Child not found", 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
            
            # Convert numeric fields
            int_fields = ['total_hours_school_days', 'total_hours_non_school_days']
            for field in int_fields:
                if field in data and data[field] is not None:
                    try:
                        data[field] = int(data[field])
                    except (ValueError, TypeError):
                        pass
            
            serializer = ChildHeavyTaskSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': "Child heavy task created successfully", 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'msg': serializer.errors, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Get all child heavy tasks",
        responses={200: ChildHeavyTaskSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            tasks = childHeavyTaskTbl.objects.all()
            serializer = ChildHeavyTaskSerializer(tasks, many=True)
            return Response({'msg': "Child heavy tasks fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Child Light Task 12 Months APIs
class ChildLightTask12MonthsAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Create child light task 12 months record",
        request_body=ChildLightTask12MonthsSerializer,
        responses={201: 'Child light task 12 months created successfully', 400: "Invalid data", 500: "Internal Server Error"}
    )
    def post(self, request):
        try:
            data = request.data.copy()
            
            # Validate foreign key relationships
            if 'task' in data:
                try:
                    task = lightTaskTbl.objects.get(id=data['task'])
                    data['task'] = task.id
                except lightTaskTbl.DoesNotExist:
                    return Response({'msg': "Light task not found", 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
            
            if 'child' in data:
                try:
                    child = ChildInHouseholdTbl.objects.get(id=data['child'])
                    data['child'] = child.id
                except ChildInHouseholdTbl.DoesNotExist:
                    return Response({'msg': "Child not found", 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
            
            # Convert numeric fields
            int_fields = ['total_hours_light_work_school', 'total_hours_light_work_non_school']
            for field in int_fields:
                if field in data and data[field] is not None:
                    try:
                        data[field] = int(data[field])
                    except (ValueError, TypeError):
                        pass
            
            # Handle MultiSelectField for performed_tasks_12months
            if 'performed_tasks_12months' in data and isinstance(data['performed_tasks_12months'], list):
                data['performed_tasks_12months'] = ','.join(data['performed_tasks_12months'])
            
            serializer = ChildLightTask12MonthsSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': "Child light task 12 months created successfully", 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'msg': serializer.errors, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Get all child light tasks 12 months",
        responses={200: ChildLightTask12MonthsSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            tasks = childLightTask12MonthsTbl.objects.all()
            serializer = ChildLightTask12MonthsSerializer(tasks, many=True)
            return Response({'msg': "Child light tasks 12 months fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Child Heavy Task 12 Months APIs
class ChildHeavyTask12MonthsAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Create child heavy task 12 months record",
        request_body=ChildHeavyTask12MonthsSerializer,
        responses={201: 'Child heavy task 12 months created successfully', 400: "Invalid data", 500: "Internal Server Error"}
    )
    def post(self, request):
        try:
            data = request.data.copy()
            
            # Validate foreign key relationships
            if 'task' in data:
                try:
                    task = heavyTaskTbl.objects.get(id=data['task'])
                    data['task'] = task.id
                except heavyTaskTbl.DoesNotExist:
                    return Response({'msg': "Heavy task not found", 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
            
            if 'child' in data:
                try:
                    child = ChildInHouseholdTbl.objects.get(id=data['child'])
                    data['child'] = child.id
                except ChildInHouseholdTbl.DoesNotExist:
                    return Response({'msg': "Child not found", 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
            
            # Convert numeric fields
            int_fields = ['total_hours_school_days', 'total_hours_non_school_days']
            for field in int_fields:
                if field in data and data[field] is not None:
                    try:
                        data[field] = int(data[field])
                    except (ValueError, TypeError):
                        pass
            
            # Handle MultiSelectField for heavy_tasks_12months
            if 'heavy_tasks_12months' in data and isinstance(data['heavy_tasks_12months'], list):
                data['heavy_tasks_12months'] = ','.join(data['heavy_tasks_12months'])
            
            serializer = ChildHeavyTask12MonthsSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg': "Child heavy task 12 months created successfully", 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'msg': serializer.errors, 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e), 'data': {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Get all child heavy tasks 12 months",
        responses={200: ChildHeavyTask12MonthsSerializer(many=True), 500: "Internal Server Error"}
    )
    def get(self, request):
        try:
            tasks = childHeavyTask12MonthsTbl.objects.all()
            serializer = ChildHeavyTask12MonthsSerializer(tasks, many=True)
            return Response({'msg': "Child heavy tasks 12 months fetched successfully", 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e), 'data': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)