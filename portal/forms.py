from django import forms
from .models import Cover_tbl

class CoverForm(forms.ModelForm):
    class Meta:
        model = Cover_tbl
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        resides = cleaned_data.get("farmer_resides_in_community")
        community_name = cleaned_data.get("community_name")
        farmer_community = cleaned_data.get("farmer_community")
        
        if resides == "No":
            if not community_name:
                self.add_error(
                    "community_name",
                    "Please provide the community name if the farmer does not reside in the cover community."
                )
            if not farmer_community:
                self.add_error( 
                    "farmer_community",
                    "Please provide the community name if the farmer does not reside in the cover community."
                )
        return cleaned_data


class FarmerAvailabilityForm(forms.ModelForm):
    class Meta:
        model = Cover_tbl
        fields = [
            'farmer_available',
            'reason_unavailable',
            'reason_unavailable_other',
            'available_answer_by',
            # include other fields as needed
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        farmer_available = cleaned_data.get("farmer_available")
        reason_unavailable = cleaned_data.get("reason_unavailable")
        reason_unavailable_other = cleaned_data.get("reason_unavailable_other")
        available_answer_by = cleaned_data.get("available_answer_by")
        
        # If the farmer is not available, require a reason.
        if farmer_available == "No":
            if not reason_unavailable:
                self.add_error(
                    "reason_unavailable",
                    "Please select a reason if the farmer is not available."
                )
            # If "Other" is selected as the reason, then require a text explanation.
            if reason_unavailable == "Other" and not reason_unavailable_other:
                self.add_error(
                    "reason_unavailable_other",
                    "Please specify the reason if 'Other' is selected."
                )
            # Optionally, you might also want to ensure that available_answer_by is provided.
            if not available_answer_by:
                self.add_error(
                    "available_answer_by",
                    "Please select who is available to answer for the farmer."
                )
        else:
            # If the farmer is available, these fields can be cleared or ignored.
            cleaned_data["reason_unavailable"] = ""
            cleaned_data["reason_unavailable_other"] = ""
            cleaned_data["available_answer_by"] = ""
        
        return cleaned_data