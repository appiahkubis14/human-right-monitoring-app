from rest_framework import serializers
from .models import (
    Cover_tbl, ConsentLocation_tbl, FarmerIdentificationtbl, AdultInHouseholdTbl, ChildInHouseholdTbl, ChildRemediationTbl,
    HouseholdSensitizationTbl, EndOfCollection
)

class CoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cover_tbl
        fields = '__all__'

class ConsentLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentLocation_tbl
        fields = '__all__'

class FarmerIdentificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerIdentificationtbl
        fields = '__all__'

# class OwnerIdentificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OwnerIdentificationTbl
#         fields = '__all__'

# class WorkerInTheFarmSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WorkerInTheFarmTbl
#         fields = '__all__'

class AdultInHouseholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdultInHouseholdTbl
        fields = '__all__'

class ChildInHouseholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildInHouseholdTbl
        fields = '__all__'

class ChildRemediationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildRemediationTbl
        fields = '__all__'

class HouseholdSensitizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseholdSensitizationTbl
        fields = '__all__'

class EndOfCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EndOfCollection
        fields = '__all__'


# Master serializer for Cover_tbl with nested related data
class CoverSyncSerializer(serializers.ModelSerializer):
    consent_location = ConsentLocationSerializer(required=False)
    farmer_identification = FarmerIdentificationSerializer(required=False)
    # owner_identification = OwnerIdentificationSerializer(required=False)
    # worker_in_farm = WorkerInTheFarmSerializer(required=False)
    adult_in_household = AdultInHouseholdSerializer(required=False)
    child_in_household = ChildInHouseholdSerializer(required=False)
    child_remediation = ChildRemediationSerializer(required=False)
    household_sensitization = HouseholdSensitizationSerializer(required=False)
    end_of_collection = EndOfCollectionSerializer(required=False)
    
    class Meta:
        model = Cover_tbl
        # Include the fields from Cover_tbl plus nested ones
        fields = (
            'id',
            'enumerator_name',       # Example field in Cover_tbl
            'enumerator_code', 
            'country',  
            'region',
            'district',
            'society',
            'society_code',
            'farmer_code',
            'farmer_surname',
            'farmer_first_name',
            'risk_classification',
            'client',
            'num_farmer_children',
            'list_children',
            
            'consent_location',
            'farmer_identification',
            # 'owner_identification',
            # 'worker_in_farm',
            'adult_in_household',
            'child_in_household',
            'child_remediation',
            'household_sensitization',
            'end_of_collection',
        )
    
    def create(self, validated_data):
        # Extract nested data
        consent_data = validated_data.pop('consent_location', None)
        farmer_data = validated_data.pop('farmer_identification', None)
        # owner_data = validated_data.pop('owner_identification', None)
        # worker_data = validated_data.pop('worker_in_farm', None)
        adult_data = validated_data.pop('adult_in_household', None)
        child_data = validated_data.pop('child_in_household', None)
        remediation_data = validated_data.pop('child_remediation', None)
        sensitization_data = validated_data.pop('household_sensitization', None)
        end_data = validated_data.pop('end_of_collection', None)
        
        cover = Cover_tbl.objects.create(**validated_data)
        
        if consent_data:
            ConsentLocation_tbl.objects.create(cover=cover, **consent_data)
        if farmer_data:
            FarmerIdentificationtbl.objects.create(cover=cover, **farmer_data)
        # if owner_data:
        #     OwnerIdentificationTbl.objects.create(cover=cover, **owner_data)
        # if worker_data:
        #     WorkerInTheFarmTbl.objects.create(cover=cover, **worker_data)
        if adult_data:
            AdultInHouseholdTbl.objects.create(cover=cover, **adult_data)
        if child_data:
            ChildInHouseholdTbl.objects.create(cover=cover, **child_data)
        if remediation_data:
            ChildRemediationTbl.objects.create(cover=cover, **remediation_data)
        if sensitization_data:
            HouseholdSensitizationTbl.objects.create(cover=cover, **sensitization_data)
        if end_data:
            EndOfCollection.objects.create(cover=cover, **end_data)
        
        return cover
    
    def update(self, instance, validated_data):
        # Update Cover_tbl fields
        instance.farmer_name = validated_data.get('farmer_name', instance.farmer_name)
        instance.farmer_address = validated_data.get('farmer_address', instance.farmer_address)
        # ... update other Cover_tbl fields as needed ...
        instance.save()
        
        # Helper to update or create a one-to-one related object
        def update_or_create_related(rel_name, serializer_class, data):
            if data:
                related_obj = getattr(instance, rel_name, None)
                if related_obj:
                    serializer_class().update(related_obj, data)
                else:
                    serializer_class().create({**data, 'cover': instance})
        
        update_or_create_related('consent_location', ConsentLocationSerializer, validated_data.pop('consent_location', None))
        update_or_create_related('farmer_identification', FarmerIdentificationSerializer, validated_data.pop('farmer_identification', None))
        # update_or_create_related('owner_identification', OwnerIdentificationSerializer, validated_data.pop('owner_identification', None))
        # update_or_create_related('worker_in_farm', WorkerInTheFarmSerializer, validated_data.pop('worker_in_farm', None))
        update_or_create_related('adult_in_household', AdultInHouseholdSerializer, validated_data.pop('adult_in_household', None))
        update_or_create_related('child_in_household', ChildInHouseholdSerializer, validated_data.pop('child_in_household', None))
        update_or_create_related('child_remediation', ChildRemediationSerializer, validated_data.pop('child_remediation', None))
        update_or_create_related('household_sensitization', HouseholdSensitizationSerializer, validated_data.pop('household_sensitization', None))
        update_or_create_related('end_of_collection', EndOfCollectionSerializer, validated_data.pop('end_of_collection', None))
        
        return instance