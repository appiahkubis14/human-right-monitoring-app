from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from portal.models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = staffTbl
        fields = '__all__'

class StaffLoginSerializer(serializers.Serializer):
    staffid = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        staffid = data.get('staffid')
        password = data.get('password')
        
        try:
            staff = staffTbl.objects.get(staffid=staffid)
            if staff.cmpassword == password:
                return data
            raise serializers.ValidationError("Invalid password")
        except staffTbl.DoesNotExist:
            raise serializers.ValidationError("Staff not found")

class ChangePasswordSerializer(serializers.Serializer):
    user = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = farmerTbl
        fields = '__all__'

class PCISerializer(serializers.ModelSerializer):
    class Meta:
        model = pciTbl
        fields = '__all__'

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = schhoolTbl
        fields = '__all__'

class HouseholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = houseHoldTbl
        fields = '__all__'

class AdultHouseholdMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdultHouseholdMember
        fields = '__all__'

# class ChildInHouseholdSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ChildInHouseholdTbl
#         fields = '__all__'



# Remove this line:
# from multiselectfield.db.fields import MSFList

# Use this simpler custom field instead:
class MultiSelectField(serializers.Field):
    def to_representation(self, value):
        if value:
            if isinstance(value, str):
                # Convert comma-separated string to list
                return [item.strip() for item in value.split(',') if item.strip()]
            elif isinstance(value, list):
                return value
        return []
    
    def to_internal_value(self, data):
        if isinstance(data, str):
            # Handle comma-separated string or JSON string
            if data.startswith('[') and data.endswith(']'):
                import json
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    # Fallback to comma-separated
                    return [item.strip() for item in data.split(',') if item.strip()]
            else:
                return [item.strip() for item in data.split(',') if item.strip()]
        elif isinstance(data, list):
            return data
        return []


# serializers.py
class ChildInHouseholdSerializer(serializers.ModelSerializer):
    performed_tasks = MultiSelectField(required=False)
    
    class Meta:
        model = ChildInHouseholdTbl
        fields = '__all__'
    
    def validate_performed_tasks(self, value):
        """Validate that all task values are valid choices"""
        if value:
            valid_tasks = []
            task_choices = dict(TASK_CHOICES)
            for task in value:
                if task in task_choices:
                    valid_tasks.append(task)
                else:
                    raise serializers.ValidationError(f"'{task}' is not a valid task choice")
            return valid_tasks
        return value

class LightTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = lightTaskTbl
        fields = '__all__'

class HeavyTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = heavyTaskTbl
        fields = '__all__'

class ChildLightTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = childLightTaskTbl
        fields = '__all__'

class ChildHeavyTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = childHeavyTaskTbl
        fields = '__all__'

class ChildLightTask12MonthsSerializer(serializers.ModelSerializer):
    class Meta:
        model = childLightTask12MonthsTbl
        fields = '__all__'

class ChildHeavyTask12MonthsSerializer(serializers.ModelSerializer):
    class Meta:
        model = childHeavyTask12MonthsTbl
        fields = '__all__'

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = regionTbl
        fields = '__all__'

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = districtTbl
        fields = '__all__'

class SocietySerializer(serializers.ModelSerializer):
    class Meta:
        model = societyTbl
        fields = '__all__'

class PriorityLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriorityLevel
        fields = '__all__'

class DeadlineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeadlineType
        fields = '__all__'

class DeadlineAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeadlineAssignment
        fields = '__all__'

class QueryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryCategory
        fields = '__all__'

class QueryPrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryPriority
        fields = '__all__'

class QueryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryStatus
        fields = '__all__'

class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = '__all__'

class QueryResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryResponse
        fields = '__all__'

class RiskAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskAssessment
        fields = '__all__'

class AuditStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditStatus
        fields = '__all__'

class AuditTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditType
        fields = '__all__'

class AuditCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditCheck
        fields = '__all__'



# Add these to your serializers.py

class LightTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = lightTaskTbl
        fields = '__all__'

class HeavyTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = heavyTaskTbl
        fields = '__all__'

class ChildLightTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = childLightTaskTbl
        fields = '__all__'

class ChildHeavyTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = childHeavyTaskTbl
        fields = '__all__'

class ChildLightTask12MonthsSerializer(serializers.ModelSerializer):
    class Meta:
        model = childLightTask12MonthsTbl
        fields = '__all__'

class ChildHeavyTask12MonthsSerializer(serializers.ModelSerializer):
    class Meta:
        model = childHeavyTask12MonthsTbl
        fields = '__all__'