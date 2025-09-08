from django.contrib import admin
from .models import (
    Cover_tbl,
    FarmerChild,
    ConsentLocation_tbl,
    FarmerIdentification_OwnerIdentificationTbl,
    FarmerIdentification_Info_OnVisit_tbl,
    WorkersInTheFarmTbl,
    AdultInHouseholdTbl,
    AdultHouseholdMember,
    ChildrenInHouseholdTbl,
    ChildInHouseholdTbl,
    ChildEducationDetailsTbl,
    ChildRemediationTbl,
    HouseholdSensitizationTbl,
    EndOfCollection,
)

# Customize the admin site headers and titles
admin.site.site_header = "REVIEW GHA - CLMRSHousehold Profiling - 24-25"
admin.site.site_title = "Child Labour Survey Admin"
admin.site.index_title = "Child Labour Survey Administration"

# ========================================================
# Group 1: Core Models
# ========================================================
class CoverAdmin(admin.ModelAdmin):
    list_display = ('enumerator_name', 'farmer_code', 'farmer_first_name', 'farmer_surname')
    search_fields = ('enumerator_name', 'farmer_code', 'farmer_first_name', 'farmer_surname')

admin.site.register(Cover_tbl, CoverAdmin)
admin.site.register(ConsentLocation_tbl)
admin.site.register(EndOfCollection)

# ========================================================
# Group 2: Farmer Identification
# ========================================================
class FarmerIdentificationAdmin(admin.ModelAdmin):
    # Adjusted to reflect fields on FarmerIdentification_OwnerIdentificationTbl
    list_display = ('owner_identification', 'name_owner', 'first_name_owner')
    search_fields = ('name_owner', 'first_name_owner')

admin.site.register(FarmerIdentification_OwnerIdentificationTbl, FarmerIdentificationAdmin)
admin.site.register(FarmerIdentification_Info_OnVisit_tbl)

# ========================================================
# Group 3: Workers & Household
# ========================================================
class WorkersInTheFarmAdmin(admin.ModelAdmin):
    list_display = ('id',)  # Customize as needed

admin.site.register(WorkersInTheFarmTbl, WorkersInTheFarmAdmin)

# Inline for AdultHouseholdMember in AdultInHouseholdTbl
class AdultHouseholdMemberInline(admin.TabularInline):
    model = AdultHouseholdMember
    extra = 1

@admin.register(AdultInHouseholdTbl)
class AdultInHouseholdAdmin(admin.ModelAdmin):
    # Changed 'cover' to 'consent' because the model has a 'consent' field.
    list_display = ('consent', 'total_adults')
    inlines = [AdultHouseholdMemberInline]

admin.site.register(ChildrenInHouseholdTbl)
admin.site.register(ChildInHouseholdTbl)
admin.site.register(ChildEducationDetailsTbl)

# ========================================================
# Group 4: Child Remediation & Sensitization
# ========================================================
admin.site.register(ChildRemediationTbl)
admin.site.register(HouseholdSensitizationTbl)

# ========================================================
# Group 5: Farmer Child
# ========================================================
admin.site.register(FarmerChild)
